# spiders/simple_spider.py (仅用于阶段一测试)
import scrapy
from news_classifier_crawler.items import NewsArticleItem
from scrapy_playwright.page import PageMethod # !!! 添加这行 !!!
import asyncio # !!! 添加这行导入 asyncio !!!

class SimpleTestSpider(scrapy.Spider):
    name = "simple_test_spider"
    #start_urls = ["https://liliputing.com/lilbits-3rd-party-steamos-devices-the-new-pebble-2-smartwatch-processor-and-sony-is-still-making-flagship-phones-with-headphone-jacks/"] # 一个简单的静态页面
    #start_urls = ["https://news.qq.com/rain/a/20250513A0972D00"] # 替换为您选择的实际 Playwright 测试 URL
    #start_urls = ["https://www.npr.org/2025/05/13/nx-s1-5391879/he-was-experiencing-psychosis-then-his-boss-made-a-decision-that-saved-his-life"] 
    start_urls = ["https://www.msn.com/en-us/news/news/content/ar-AA1EDOkc?ocid=superappdhp&muid=565EC11999DC42C793A289F15C6712B8&adid=&anid=&market=en-us&cm=en-us&activityId=9400A456E37A40BB885059CE0D2BD64A&bridgeVersionInt=115&fontSize=sa_fontSize&isChinaBuild=false"]


    # 最简单的爬虫
    # def parse(self, response):
    #     self.logger.info(f"Crawled URL: {response.url}")
    #     self.logger.info(f"Response Status: {response.status}")
    #
    #     # 创建 Item
    #     # item = NewsArticleItem()
    #     # item['url'] = response.url # 只赋值 URL 字段
    #
    #     # Yield Item
    #     # self.logger.info(f"DEBUG: Yielding item for URL: {item['url']}")
    #     # yield item

    def start_requests(self):
        # 手动创建并 Yield Playwright 请求
        for url in self.start_urls:
            self.logger.info(f"DEBUG: Yielding Playwright start request for URL: {url}")
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,  # !!! 启用 Playwright !!!
                    'playwright_include_page': True, # 可选，如果需要在回调中直接操作 page 对象
                    'playwright_page_methods': [ # 添加等待页面加载状态的方法
                         # 等待网络空闲，通常是可靠的等待方式
                         PageMethod('wait_for_load_state', 'networkidle'),
                         # 或者等待某个关键元素出现 (如果知道选择器的话)
                         # PageMethod('wait_for_selector', 'div.article-body'),
                    ],
                },
                callback=self.parse_rendered_page, # Playwright 渲染后，回调到这里
                errback=self.on_error # 添加错误处理
            )

    # 定义处理 Playwright 渲染后响应的异步方法
    async def parse_rendered_page(self, response):
        self.logger.info(f"DEBUG: >>> Entering parse_rendered_page for URL: {response.url}") # 确认进入

         # 打印获取到的 HTML 内容片段和长度
        if response.text:
            self.logger.info(f"DEBUG: Rendered HTML length for {response.url}: {len(response.text)}")
            self.logger.info(f"DEBUG: Rendered HTML snippet for {response.url}: {response.text[:500]}...") # 打印前500字符
        else:
            self.logger.warning(f"DEBUG: Rendered HTML is EMPTY for {response.url}.")

         # 等待 domcontentloaded
        try:
            self.logger.info(f"DEBUG: Playwright Handler: Waiting for domcontentloaded for {response.url}")
            await response.page.wait_for_load_state('domcontentloaded', timeout=self.settings.getint('PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT')) # 使用 settings 中的超时
            self.logger.info(f"DEBUG: Playwright Handler: Load state 'domcontentloaded' reached for {response.url}")
        except Exception as e:
            self.logger.warning(f"DEBUG: Playwright Handler: Waiting for domcontentloaded failed for {response.url}: {e}. Continuing.")

        # 添加一个固定的延时
        delay_seconds = 5 # 例如等待 5 秒
        self.logger.info(f"DEBUG: Playwright Handler: Adding fixed delay ({delay_seconds}s) for {response.url}")
        await asyncio.sleep(delay_seconds)
        self.logger.info(f"DEBUG: Playwright Handler: Fixed delay finished for {response.url}")

        item = NewsArticleItem()
        item['url'] = response.url
        item['rendered_html'] = response.text # 将渲染后的 HTML 保存到 Item

        # 打印获取到的 HTML 长度
        if response.text:
            self.logger.info(f"DEBUG: Rendered HTML length for {response.url}: {len(response.text)}")
        else:
            self.logger.warning(f"DEBUG: Rendered HTML is EMPTY for {response.url}")

        # 暂时不 Yield Item，先确认能获取到渲染后的 HTML
        self.logger.info(f"DEBUG: >>> Yielding item for URL: {item['url']}") # 确认 Item 被 Yield
        #yield item

    # 定义错误处理方法
    async def on_error(self, failure):
         request = failure.request
         self.logger.error(f"DEBUG: !!! Playwright Request failed for {request.url}: {failure.getErrorMessage()}")
         # Optionally log the URL to a file