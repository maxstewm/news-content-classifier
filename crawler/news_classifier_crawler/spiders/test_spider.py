# spiders/eval_spider.py (仅用于测试)
import scrapy
# 暂时不需要 LinkExtractor 和 CrawlSpider
# from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider, Rule

# 导入 Item
from news_classifier_crawler.items import NewsArticleItem

# 暂时不需要 urlparse
# from urllib.parse import urlparse
# 暂时不需要 logging
# import logging

# 使用 scrapy.Spider 作为基础，最简单
class EvaluationSpider(scrapy.Spider):
    name = "test_spider"

    # 仅抓取一个简单的、不需要 JS 渲染的页面进行测试
    # 例如 Scrapy 官方文档的例子网站
    start_urls = ["http://quotes.toscrape.com/"]

    # 暂时移除域名限制和计数器
    # allowed_domains = [...]
    # crawled_count_per_domain = {}
    # page_limit_per_domain = 100

    # 移除 __init__ 方法 (如果只包含计数器初始化)
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     ...

    # 移除 rules (CrawlSpider 特有)
    # rules = (...)

    # 移除 process_links 方法
    # def process_links(self, response, links):
    #     ...

    # 移除 parse_rendered_article 方法 (因为暂时不用 Playwright)
    # async def parse_rendered_article(self, response):
    #     ...

    # 重写 parse 方法，处理简单的响应
    # 注意：这里是处理普通 Response，而不是 Playwright 渲染后的 Response
    # 也暂时移除 Playwright meta
    def parse(self, response):
        self.logger.info(f"Crawled URL: {response.url}")
        self.logger.info(f"Response Status: {response.status}")

        # 创建 Item
        item = NewsArticleItem()
        item['url'] = response.url
        # 暂时不抓取 HTML 内容
        # item['html_content'] = response.text
        # item['rendered_html'] = "" # 暂时留空或移除

        # 提取一些简单字段作为测试
        item['title'] = response.css('title::text').get()
        item['description'] = response.css('meta[name="description"]::attr(content)').get() # 这个网站可能没有 description

        # 在 Item 中添加一个测试字段，用于确认 Item 已被 Yield
        #item['test_field'] = "This is a test item"

        # Yield Item，它会进入 Pipeline (如果 Pipeline 启用了)
        yield item

        # 暂时移除提取链接和 Follow 的逻辑
        # links = response.css('a::attr(href)').getall()
        # for link in links:
        #    yield response.follow(link, self.parse)