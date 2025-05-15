# settings.py

BOT_NAME = "news_classifier_crawler"

SPIDER_MODULES = ["news_classifier_crawler.spiders"]
NEWSPIDER_MODULE = "news_classifier_crawler.spiders"

# Obey robots.txt rules - IMPORTANT for ethical crawling
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Set a real User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36' # 使用一个常见的浏览器 UA


# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2 # Be polite, wait 2 seconds between requests to the same domain
# The download delay setting will only work when AUTO_THROTTLE is disabled.

DOWNLOAD_HANDLERS_BASE = {
    # 这里列出 Scrapy 默认的 handler，Playwright 会覆盖 http/https
    # 默认 handlers 可以参考 scrapy 官方文档，或者不设置这个，让 Scrapy 自己合并
}

#simple_spider设置
#DOWNLOAD_HANDLERS_BASE = None

# Explicitly list the download handlers and their order
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    # 保留其他可能的 handler，例如 file:// 等，但确保 http/https 是 Playwright
    # "file": "scrapy.core.downloader.handlers.file.FileDownloadHandler",
    # "s3": "scrapy.core.downloader.handlers.s3.S3DownloadHandler",
}

# Playwright settings
PLAYWRIGHT_BROWSER_TYPE = "chromium" # 'chromium', 'firefox' or 'webkit'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True, # Run browser in headless mode
    "timeout": 120000, # 20 seconds timeout
    # Optional: Add args that might help with stability
    "args": ["--no-sandbox", "--disable-setuid-sandbox"], # 有时在Linux容器环境有用
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 1200000 # 30 seconds timeout for page navigation
PLAYWRIGHT_DEFAULT_LOAD_STATE = 'domcontentloaded' # 默认等待 'load'，或者改为 'domcontentloaded', 'networkidle'

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "news_classifier_crawler.middlewares.NewsClassifierCrawlerSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# Disable middlewares that might filter requests before Playwright handler
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None, # 禁用 Robots.txt 中间件
    'scrapy.downloadermiddlewares.offsite.OffsiteMiddleware': None,   # 禁用 Offsite 中间件
    'scrapy.downloadermiddlewares.dupefilter.DupeFilter': None,       # 禁用去重中间件
    # 保留其他默认中间件，或根据需要启用您自定义的中间件
    # 'scrapy_playwright.middleware.PlaywrightMiddleware': 725, # 确保这个没有被启用（因为新版已移到 handler 内部）
    # ... 其他您可能添加的中间件 ...
}

DOWNLOADER_MIDDLEWARES['scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware'] = None # 即使设置 False，禁用中间件更直接排除问题

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "news_classifier_crawler.pipelines.ContentExtractionPipeline": 300, # Your custom pipeline
   # "news_classifier_crawler.pipelines.NewsClassifierCrawlerPipeline": 300, # Example default pipeline
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending to each remote server at any period of time
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings depending on the environment (optional)
# if os.environ.get("CI"):
#     PLAYWRIGHT_LAUNCH_OPTIONS["headless"] = True

# Output format - configure this later to export as JSON Lines for Label Studio
FEED_FORMAT = 'jsonlines'
#FEED_URI = 'crawled_data.jsonl'

# Configure the reactor to use asyncio
# This is required by scrapy-playwright
# See https://docs.scrapy.org/en/latest/topics/asyncio.html
# And https://github.com/scrapy-plugins/scrapy-playwright#installation
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
LOG_LEVEL = 'DEBUG' #DEBUG 'INFO'

PLAYWRIGHT_ABORT_REQUEST = 'news_classifier_crawler.settings.should_abort_request' # 指定请求拦截方法

# 在 settings.py 文件末尾，定义请求拦截方法
def should_abort_request(request):
     # 将您在日志中看到的、与广告和跟踪相关的 URL 或域名添加到黑名单
     aborted_resource_types = ["image", "font", "media", "xhr", "fetch", "script", "stylesheet", "document"] # 拦截所有类型的资源

     # 常见的广告、跟踪、社交媒体等域名黑名单
     aborted_domains = [
         # Google Ads/Analytics
         'doubleclick.net', 'google-analytics.com', 'googletagmanager.com', 'googlesyndication.com', 'googleadservices.com', 'gstatic.com',
         # Rubicon Project
         'rubiconproject.com', 'tap.php', 'eus.rubiconproject.com', 'rp.gwallet.com',
         # PubMatic
         'pubmatic.com', 'pubmatic.com.cn', 'simage2.pubmatic.com', 'simage4.pubmatic.com',
         # Media.net
         'media.net', 'hbx.media.net', 'hb2.media.net',
         # Criteo
         'criteo.com', 'grid-bidder.criteo.com',
         # AppNexus (Xandr)
         'adnxs.com',
         # Index Exchange
         'indexww.com',
         # 其他广告/跟踪/社交媒体域名
         'casalemedia.com', 'adthrive.com', 'permutive.com', 'chartbeat.net', 'scorecardresearch.com', 'liadm.com', 'tapad.com', 'connatix.com', 'onetrust.com', 'cookielaw.org', 'adsrvr.org', 'bidr.io', 'semasio.net', 'openx.net', 'imrworldwide.com', 'liadm.com', 'sandstrophies.com', 'micro.rubiconproject.com', 'metrics.adform.net', 'ads.pubmatic.com', 'secure-sdk.imrworldwide.com', 'securepubads.g.doubleclick.net', 'rhythmone.com', 'voicefive.com', 'crwdcntrl.net', 'tynt.com', 'clearnview.com', 'yieldmo.com', 'rtb.openx.net', 'pr-bh.ybp.yahoo.com', 'sync.targeting.unrulymedia.com', 'sync.adkernel.com', 'usersync.analytics.yahoo.com', 'simage2.pubmatic.com', 'u.openx.net', 'cs.krushmedia.com', 'csync.loopme.me', 'match.justpremium.com', 'crb.kargo.com', 'sync.cootlogix.com', 'sync.aniview.com', 'usersync.getpublica.com', 'pixel.servebom.com', 's.seedtag.com', 'match.sharethrough.com', 'ads.stickyadstv.com', 'udmserve.net', 'usync.vrtcal.com', 'ums.acuityplatform.com', 'c1.adform.net', 'inv-nets.admixer.net', 'b1sync.zemanta.com', 'pixel-sync.sitescout.com', 'unruly-match.dotomi.com', 'dis.criteo.com', 'ads.blogherads.com', # 您之前看到的博客广告域名
         'twitter.com', 'platform.twitter.com', # Twitter Embed
         # 腾讯相关域名 (如果您不希望抓取 QQ 的跟踪)
         'qq.com', 'gtimg.com', 'beacon.qq.com', 'trace.qq.com', 'qpic.cn', 'qimei.qq.com',
         # 其他可能不需要的资源域名
         'use.typekit.net', # 字体加载
         'cdnjs.cloudflare.com', # CDN 上的库
         'jsdelivr.net', # CDN
         'code.jquery.com', # jQuery CDN
         'w.org', # WordPress API
         'wp.com', # WordPress stats
         'youtube.com', 'youtu.be', # YouTube 视频 (如果不需要)
         'vimeo.com', # Vimeo 视频 (如果不需要)
         'jwplayer.com', # 视频播放器
         'adzerk.net', # 广告服务
         'adnxs.com', 'advertising.com', 'casalemedia.com', 'contextweb.com', 'doubleverify.com', 'everesttech.net', 'imrworldwide.com', 'krxd.net', 'liveintent.com', 'media.net', 'mediamath.com', 'openx.net', 'rubiconproject.com', 'scorecardresearch.com', 'sharethrough.com', 'simpli.fi', 'spotx.tv', 'swoop.com', 'taboola.com', 'tap.fmpub.net', 'tapad.com', 'tremorhub.com', 'trustarc.com', 'videology.com', 'yieldmo.com', 'zemanta.com', 'zyppah.com', # 其他常见的广告/跟踪域名
         'fontawesome.com', 'bootstrapcdn.com', # CDN 上的字体或库
         'google.com/recaptcha', 'www.recaptcha.net', # 验证码相关
         'cloudflare.com/cdn-cgi', # Cloudflare Challenges
         # 添加更多您在日志中看到的、不需要的资源 URL 部分或域名
     ]

     # 检查请求的 URL 是否包含黑名单中的任何域名
     if any(domain in request.url for domain in aborted_domains):
         # 如果是黑名单中的资源类型和域名，则拦截
         return True

     # 您也可以根据 URL 路径来拦截特定类型的页面 (在 CrawlSpider 中 LinkExtractor 更灵活)
     # if "api.permutive.com" in request.url and "/v2.0/watson" in request.url:
     #     return True # 例如拦截 Permutive 的特定 API 请求

     # 默认不拦截
     return False
