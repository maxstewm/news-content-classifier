# spiders/eval_spider.py
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from news_classifier_crawler.items import NewsArticleItem
from urllib.parse import urlparse
import logging
from scrapy_playwright.page import PageMethod # 添加这行
import asyncio # 添加这行
#from scrapy_playwright.page import PageCoroutine


class EvaluationSpider(CrawlSpider):
    name = "eval_spider"

    # Define the 20 core domains for evaluation
    # IMPORTANT: Replace with your actual 20 domains
  
    core_domains = [

    #"msn.com",
    "npr.org", 
    "bleacherreport.com",
    "variety.com",
    "hollywoodreporter.com",
    "webmd.com",
    "statnews.com",
    "sciencedaily.com",
    "politico.com",

        # Add your specific core domains here
    ]
 

    allowed_domains = core_domains
    #start_urls = [f"https://www.{domain}" for domain in core_domains]
    #start_urls = [f"https://www.{domain}" for domain in core_domains] # 确保这行是有效的，且 core_domains 非空

    start_urls = [
        #"https://liliputing.com/lilbits-3rd-party-steamos-devices-the-new-pebble-2-smartwatch-processor-and-sony-is-still-making-flagship-phones-with-headphone-jacks/",
        #"https://www.msn.com/en-us/news/news/content/ar-AA1EDOkc?ocid=superappdhp&muid=565EC11999DC42C793A289F15C6712B8&adid=&anid=&market=en-us&cm=en-us&activityId=9400A456E37A40BB885059CE0D2BD64A&bridgeVersionInt=115&fontSize=sa_fontSize&isChinaBuild=false" # 添加 QQ 新闻 URL 作为对照
        # 您可以添加其他已知可以成功的 URL 到这个列表进行测试
        #"https://www.msn.com/en-us/news", # MSN 新闻首页
        "https://www.npr.org/sections/news/", # NPR 新闻首页
        "https://www.npr.org/2025/05/13/nx-s1-5391879/he-was-experiencing-psychosis-then-his-boss-made-a-decision-that-saved-his-life",
        "https://www.npr.org/2025/05/13/nx-s1-5397310/pete-rose-shoeless-joe-jackson-lifts-ban-hall-of-fame",
        "https://liliputing.com/", # Liliputing 首页
    ]

    # Counter to limit pages per domain
    crawled_count_per_domain = {}
    #page_limit_per_domain = 100 # Target 100 pages per domain
    page_limit_per_domain = 400 # Target 100 pages per domain

    # Define rules for following links
    

    # !!! 取消注释原来的 rules 定义 !!!
    # rules = (
    #     # Rule(
    #     #     LinkExtractor(
    #     #         # allow_domains=allowed_domains, # 限制在允许的域名内
    #     #         # # 完善 LinkExtractor 的 allow 和 deny 规则 (保留您之前完善的规则)
    #     #         # allow=(
    #     #         #     r'/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/]+/$',
    #     #         #     r'/article/',
    #     #         #     r'/story/',
    #     #         #     r'/news/',
    #     #         #     r'/vip/',
    #     #         #     r'/20[0-9]{2}/',
    #     #         #     r'/content/ar-AA', # 针对 MSN 的文章 URL 模式
    #     #         #     r'/story/_/id/', # 针对 ESPN 的文章 URL 模式
    #     #         #     r'/nx-s1-\d+/', # 针对 NPR 的文章 URL 模式
    #     #         #     r'/lilbits-', # 针对 Liliputing 的文章 URL 模式
    #     #         #     # 添加更多您目标网站的文章 URL 模式
    #     #         # ),
    #     #         # deny=(
    #     #         #     r'/author/', r'/tag/', r'/category/', r'/about/', r'/contact/', r'/careers/', r'/shop/',
    #     #         #     r'/subscribe/', r'/login/', r'/register/', r'/privacy/', r'/terms/', r'/sitemap.xml',
    #     #         #     r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$', r'\.css$', r'\.js$',
    #     #         #     r'/videos/', r'/photos/', r'/gallery/',
    #     #         #     r'#',
    #     #         #     r'/index.html', r'/default.htm',
    #     #         #     r'/\d+/$', # 排除简单的分页链接，除非您需要分页
    #     #         #     r'/live-updates/',
    #     #         #     r'/scoreboard/', r'/rankings/', r'/teams/', r'/players/', r'/stats/', r'/standings/',
    #     #         #     r'/draft/', r'/free-agency/', r'/trades/',
    #     #         #     r'/podcasts/', r'/audio/', r'/video/', r'/photos/', r'/galleries/',
    #     #         #     r'/shop/', r'/subscribe/', r'/donate/', r'/contact-us/', r'/about-us/',
    #     #         #     r'/terms-of-service/', r'/privacy-policy/',
    #     #         #     r'/cdn-cgi/', r'/cloudflare/',
    #     #         #     r'/robots.txt',
    #     #         #     # 添加更多您观察到的非文章页面的 URL 模式
    #     #         # ),
    #     #     # ),
    #     #     # # 回调到处理渲染后页面的方法
    #     #     # callback="parse_rendered_article", 
    #     #     # follow=True # 继续递归抓取符合规则的链接
    #     # ),
    #      # # 您可以根据需要添加其他 Rule 来处理分页链接等
    #      # # Rule(LinkExtractor(allow=(r'page/\d+/', r'/c/\w+/page/\d+')), follow=True),
    # )

    def __init__(self, *args, **kwargs):
        super(EvaluationSpider, self).__init__(*args, **kwargs)
        # Initialize the counter for all domains
        for domain in self.core_domains:
            self.crawled_count_per_domain[domain] = 0
        self.logger.info(f"Evaluation spider started. Target {self.page_limit_per_domain} pages per domain.")
        self.logger.info(f"DEBUG: Initial start_urls: {self.start_urls}")
        self.logger.info(f"DEBUG: Length of start_urls: {len(self.start_urls)}")

        # !!! 添加 LinkExtractor 实例的创建 !!!
        self.link_extractor = LinkExtractor(
             allow_domains=self.allowed_domains,
             allow=( # 使用您之前完善的 allow 规则
                r'/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/]+/$', # 示例: /YYYY/MM/DD/slug/
                r'/article/',
                r'/story/',
                r'/news/',
                r'/vip/', # variety.com 的VIP文章
                r'/20[0-9]{2}/', # 包含年份的链接，很可能是文章
                r'/content/ar-AA', # 针对 MSN 的文章 URL 模式
                r'/story/_/id/', # 针对 ESPN 的文章 URL 模式
                r'/nx-s1-\d+/', # 针对 NPR 的文章 URL 模式
                r'/lilbits-', # 针对 Liliputing 的文章 URL 模式
                # 添加更多您目标网站的文章 URL 模式
             ),
             deny=( # 使用您之前完善的 deny 规则
                r'/author/', r'/tag/', r'/category/', r'/about/', r'/contact/', r'/careers/', r'/shop/',
                r'/subscribe/', r'/login/', r'/register/', r'/privacy/', r'/terms/', r'/sitemap.xml',
                r'\.pdf$', r'\.jpg$', r'\.png$', r'\.gif$', r'\.css$', r'\.js$', # 排除文件链接
                r'/videos/', r'/photos/', r'/gallery/', # 排除多媒体页面 (如果不需要)
                r'#', # 排除页面内部锚点
                r'/index.html', r'/default.htm', # 排除首页文件
                r'/\d+/$', # 排除简单的分页链接
                r'/live-updates/', r'/scoreboard/', r'/rankings/', r'/teams/', r'/players/', r'/stats/', r'/standings/',
                r'/draft/', r'/free-agency/', r'/trades/', r'/podcasts/', r'/audio/', r'/video/', r'/photos/', r'/galleries/',
                r'/shop/', r'/subscribe/', r'/donate/', r'/contact-us/', r'/about-us/', r'/terms-of-service/', r'/privacy-policy/',
                r'/cdn-cgi/', r'/cloudflare/', r'/robots.txt',
                # 添加更多您在日志中看到的广告/跟踪域名到 deny 列表中
                 'doubleclick.net', 'google-analytics.com', 'googletagmanager.com', 'googlesyndication.com', 'googleadservices.com', 'gstatic.com',
                 'rubiconproject.com', 'casalemedia.com', 'adthrive.com', 'permutive.com', 'chartbeat.net', 'scorecardresearch.com',
                 'liadm.com', 'tapad.com', 'connatix.com', 'onetrust.com', 'cookielaw.org', 'adsrvr.org', 'bidr.io', 'semasio.net', 'openx.net', 'imrworldwide.com', 'micro.rubiconproject.com', 'metrics.adform.net', 'ads.pubmatic.com', 'secure-sdk.imrworldwide.com',
                 'rhythmone.com', 'voicefive.com', 'crwdcntrl.net', 'tynt.com', 'clearnview.com', 'yieldmo.com', 'rtb.hhkld.com',
                 'bidadx.net', 'criteo.com', 'adnxs.com', 'ads.servenobid.com', 'simpli.fi', 't.co', 'tpc.googlesyndication.com', 'securepubads.g.doubleclick.net', 'ad.turn.com',
                 'unruly.com', 'vrtcal.com', 'sync.intentiq.com', 'sync.taboola.com', 'sync.cootlogix.com', 'sync.aniview.com', 'sync.springserve.com',
                 'sync.metrics.adform.net', 'sync.dotomi.com', 'sync.richaudience.com', 'sync.smartadserver.com', 'sync.teads.tv', 'sync.connectad.io',
                 'sync.programattic.com', 'sync.pubmatic.com', 'sync.semasio.net', 'sync.taboola.com', 'sync.targeting.unrulymedia.com', 'sync.spotim.market',
                 'sync.trustx.org', 'sync.vrtcal.com', 'sync.yieldmo.com', 'sync.yieldnexus.com', 'sync.zetassp.com', 'sync.zendo.com',
                 'cs.iad-data.com', 'cs.parrable.com', 'cs.permutive.com', 'cs.scorecardresearch.com', 'cs.simpli.fi', 'cs.steelhouse.com', 'cs.zemanta.com',
                 'twitter.com', 'platform.twitter.com', # Twitter Embed
                 'use.typekit.net', 'cdnjs.cloudflare.com', 'jsdelivr.net', 'code.jquery.com', 'w.org', 'wp.com', 'youtube.com', 'youtu.be', 'vimeo.com', 'jwplayer.com', 'adzerk.net',
                 'google.com/recaptcha', 'www.recaptcha.net', 'cloudflare.com/cdn-cgi',
                 'c2.piano.io/api','s.ad.smaato.net/c',
                 # ... 添加更多您在日志中看到的、不需要抓取的域名
                 r'/api/',
             ),
        )
        
    def start_requests(self):
        # 覆盖 start_requests 方法，为起始 URL 添加 Playwright meta
        self.logger.info("DEBUG: Generating start requests with Playwright meta.")
        self.logger.info(f"DEBUG: start_urls in start_requests: {self.start_urls}")
        self.logger.info(f"DEBUG: Length of start_urls in start_requests: {len(self.start_urls)}")
        for url in self.start_urls: # 使用类级别的 start_urls 定义的列表
            self.logger.info(f"DEBUG: Yielding Playwright start request for URL: {url}")
            yield scrapy.Request(
                url=url,
                meta=dict(
                    playwright=True, # !!! 为起始请求添加 Playwright meta !!!
                    playwright_include_page=True,
                    # 对于起始请求，核心域名键直接从 URL 解析
                    playwright_page_methods=[ # 添加等待页面加载状态的方法
                         # 尝试 'networkidle'
                         PageMethod('wait_for_load_state', 'networkidle'),
                         # 如果 networkidle 不行，可以尝试 PageMethod('wait_for_load_state', 'domcontentloaded'),
                         # 如果等待特定元素出现更可靠，可以替换为 PageMethod('wait_for_selector', '你的CSS选择器'),
                    ],
                    core_domain_key=urlparse(url).netloc.replace("www.", ""),
                    is_start_request=True # 添加这个 meta，方便后续识别起始请求
                ),
                callback=self.parse_rendered_article, # 起始页也直接进入渲染处理方法
                errback=self.on_playwright_error,
                priority=100 # 可以给起始请求更高优先级
                
            )

    

    # 重命名 parse_article 方法，使其专门负责 Yield Playwright Request
    """ async def request_playwright_rendering(self, response):
         # Use urlparse to get the domain name from the URL
        try:
            current_domain = urlparse(response.url).netloc.replace("www.", "")
        except Exception as e:
            self.logger.warning(f"Could not parse domain from {response.url} in request_playwright_rendering: {e}")
            return # 如果域名解析失败，直接返回，不处理


        # --- Check if the domain is one of our core domains ---
        # 我们在这里不进行页面数量限制和计数，只 Yield Playwright Request
        # 让 parse_rendered_article 负责计数和限制 Item Yield
        if current_domain not in self.crawled_count_per_domain:
             # 如果不是核心域名，则根据需要决定是否 Yield Playwright Request
             # 目前逻辑是非核心域名不计数不 Yield Item，这里可以选择不 Yield Playwright Request
             self.logger.debug(f"DEBUG: Skipping Playwright Request for non-core domain: {current_domain} from URL {response.url}")
             return # 非核心域名直接返回，不 Yield Playwright Request


        # --- Yield Playwright request ---
        self.logger.debug(f"DEBUG: Yielding Playwright Request for URL: {response.url}") # !!! 打印 Yield 前的状态 !!!

        yield scrapy.Request(
            url=response.url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                 playwright_page_methods=[ # 添加等待页面加载状态的方法 (确保列表内容符合您的测试)
                     # 尝试 'networkidle'
                     PageMethod('wait_for_load_state', 'networkidle'),
                     # 或者等待特定元素出现 (如果知道选择器的话)
                     # PageMethod('wait_for_selector', '你的CSS选择器'),
                     # 或者 'domcontentloaded'
                     # PageMethod('wait_for_load_state', 'domcontentloaded'),
                     # 如果使用固定延时，需要 import asyncio
                     # await asyncio.sleep(5) # 注意：延时不能放在 playwright_page_methods 里，要放在 parse_rendered_page 或 handler 里
                ],
                core_domain_key=current_domain # Pass the core domain key
            ),
            callback=self.parse_rendered_article, # 回调到渲染方法
            errback=self.on_playwright_error, # 失败时调用
            priority=10 # 可以调整优先级
        ) """
    async def block_resource_types(self, route, request):
        url = request.url
        if (
            "c2.piano.io" in url
            or "s.ad.smaato.net" in url
            or request.resource_type in ["image", "media", "stylesheet", "font", "ping", "script"]
        ):
            await route.abort()
        else:
            await route.continue_()

     # !!! 添加这个新的错误处理方法 !!!
    async def on_playwright_error(self, failure):
         # failure 是一个 twisted.python.failure.Failure 对象
         # 它可以包含异常信息
         request = failure.request # 获取失败的请求对象
         self.logger.error(f"DEBUG: !!!!!!!!!!! Playwright Request failed for {request.url}: {failure.getErrorMessage()}") # 打印错误信息
         # 可以 Yield 一个 Item 来记录失败的 URL 和错误信息
         # item = NewsArticleItem()
         # item['url'] = request.url
         # item['error_message'] = failure.getErrorMessage()
         # yield item

    async def parse_rendered_article(self, response):
        # This method receives the response *after* Playwright rendering
        # Get the original core domain key from meta
        self.logger.info(f"DEBUG: >>> Entering parse_rendered_article for URL: {response.url}") # 确认方法被调用
        current_domain = response.meta.get('core_domain_key') # 从 meta 中获取核心域名

        page = response.meta["playwright_page"]

        # 过滤请求逻辑
        await page.route("**/*", route_intercept)

        # 在回调方法中添加固定的延时
        delay_seconds = 5 # 例如等待 5 秒
        self.logger.info(f"DEBUG: Waiting for fixed delay ({delay_seconds}s) in callback for {response.url}")
        await asyncio.sleep(delay_seconds)
        self.logger.info(f"DEBUG: Fixed delay finished in callback for {response.url}")

        # --- Perform Counting and Limiting here, BEFORE Yielding Item ---
        try:# Check if it's a core domain and hasn't reached the limit
            if current_domain and current_domain in self.crawled_count_per_domain:
                if self.crawled_count_per_domain[current_domain] < self.page_limit_per_domain:
                    # Increment count ONLY when we are about to process this item for a core domain within limit
                    self.crawled_count_per_domain[current_domain] += 1
                    self.logger.info(f"Processing and COUNTING page {self.crawled_count_per_domain[current_domain]}/{self.page_limit_per_domain} for {current_domain}: {response.url}")

                    # --- Create and Yield Item ---
                    item = NewsArticleItem()
                    item['url'] = response.url
                    # 暂时不保存原始 HTML
                    # item['html_content'] = response.request.body.decode(response.encoding) if response.request.body else ""
                    item['rendered_html'] = response.text # 保存渲染后的 HTML

                    # --- Extract basic metadata using Scrapy Selectors from rendered HTML ---
                    #item['title'] = response.css('title::text').get()
                    #item['description'] = response.css('meta[name="description"]::attr(content)').get()
                    # Add other metadata extraction here...
                    #if not item['rendered_html']:
                        #self.logger.warning(f"DEBUG: Rendered HTML is EMPTY for {response.url}. Item will still be yielded (to Pipeline).") # 如果渲染结果是空的


                    if not item['rendered_html'] or len(item['rendered_html']) < 100: # 示例：长度小于100就警告
                        self.logger.warning(f"DEBUG: Rendered HTML seems too short for {response.url}. Length: {len(item['rendered_html'])}")
                    # Item will now go through the pipeline for Content Extraction (Trafilatura, spaCy)
                    self.logger.info(f"DEBUG: >>> Yielding item for URL: {response.url}") # 确认 Item 被 Yield
                    yield item

                    """ # --- 手动提取 Link 和 Yield 新请求 --- !!! 代码位置不变，但确认逻辑正确 !!!
                    self.logger.debug(f"DEBUG: Extracting links from {response.url}")
                    links = self.link_extractor.extract_links(response) # 从 Playwright Response 中提取链接
                    self.logger.debug(f"DEBUG: Extracted {len(links)} links from {response.url}")

                    # Yield 新的请求
                    for link in links:
                        try:
                            self.logger.debug(f"DEBUG: Processing extracted link: {link.url}") # 添加打印
                            # 检查提取到的链接是否仍然在 allowed_domains 内 (LinkExtractor 已经做了，但再次确认更安全)
                            parsed_link_url = urlparse(link.url)
                            link_domain = parsed_link_url.netloc.replace("www.", "")
                            if link_domain in self.allowed_domains:
                                self.logger.debug(f"DEBUG: Yielding next request: {link.url}")
                                # 为提取到的链接 Yield Playwright 请求 (回到 Playwright 流程)
                                yield scrapy.Request(
                                    url=link.url,
                                    meta=dict( # 使用 dict() 创建字典
                                        playwright=True, # !!! 确保为 True !!!
                                        playwright_include_page=True,
                                        playwright_page_methods=[ # 添加等待页面加载状态的方法
                                            PageMethod('wait_for_load_state', 'networkidle'),
                                        ],
                                        core_domain_key=urlparse(link.url).netloc.replace("www.", ""), # 添加域名键
                                        is_start_request=True
                                    ),
                                    callback=self.parse_rendered_article, # 回调到同一个处理方法
                                    errback=self.on_playwright_error, # 失败时调用
                                    priority=100 # 可以调整优先级
                                )
                            else:
                                self.logger.debug(f"DEBUG: Filtering out disallowed domain link: {link.url}")
                        except Exception as e: # !!! 添加 except 块 !!!
                            self.logger.error(f"DEBUG: !!! An ERROR occurred while processing link {link.url}: {e}")
                            # 您可以选择在这里 Yield 一个 Item 来记录链接处理失败 """
                        
                else:
                 # Domain limit reached, just log and do not yield item
                    self.logger.info(f"Skipping ITEM yield for {response.url} as domain limit already reached for {current_domain}")
            else:
                # Not a core domain, just log and do not yield item
                self.logger.debug(f"Skipping ITEM yield for non-core/untracked domain: {current_domain} from URL {response.url}")
        except Exception as e:
            self.logger.error(f"DEBUG: !!! An ERROR occurred in parse_rendered_article for {response.url}: {e}") # 捕获异常并打印
            # 可以在这里 Yield 一个带有错误信息的 Item 用于记录

    async def route_intercept(route, request):
        if (
            "c2.piano.io" in request.url or
            "s.ad.smaato.net" in request.url or
            request.resource_type in ["image", "media", "font", "stylesheet"]
        ):
            self.logger.info("abort() for : {response.url}")
            await route.abort()
        else:
            await route.continue_()

    # Optional: Override closed method to report final counts
    def closed(self, reason):
        self.logger.info("Spider closed. Final counts per domain:")
        for domain, count in self.crawled_count_per_domain.items():
             self.logger.info(f"  {domain}: {count} pages")