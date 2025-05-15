# spiders/news_spider.py
import scrapy
from news_classifier_crawler.items import NewsArticleItem

class NewsSpider(scrapy.Spider):
    name = "news_spider"
    # allowed_domains will be set dynamically or managed by CrawlSpider for eval set
    # start_urls will be set dynamically or managed by CrawlSpider for eval set

    def start_requests(self):
        # This is where you'd yield initial requests.
        # For a simple test, let's yield one request requiring Playwright
        test_url = "https://www.example.com" # Replace with a real dynamic news page URL

        # To use Playwright, set 'playwright': True in the meta dictionary
        yield scrapy.Request(
            url=test_url,
            meta=dict(
                playwright=True,
                playwright_include_page=True, # Keep the page object accessible in the response
                playwright_page_methods=[
                    # You can add methods here to interact with the page before scraping
                    # For example: {"method": "wait_for_selector", "selector": "div.article-body"},
                    # {"method": "evaluate", "script": "window.scrollBy(0, document.body.scrollHeight)"},
                    # {"method": "wait_for_load_state", "state": "networkidle"},
                ]
            ),
            callback=self.parse # Use the parse method to process the response
        )

    async def parse(self, response):
        # response.selector contains the Selector over the rendered HTML by default
        # Access the original Playwright page if needed: page = response.meta["playwright_page"]

        item = NewsArticleItem()
        item['url'] = response.url
        # item['html_content'] = response.text # This might be the pre-render HTML or base HTML
        item['rendered_html'] = response.text # response.text contains the rendered HTML when using playwright=True

        # --- Extract basic metadata using Scrapy Selectors ---
        # Extract title from the <title> tag
        item['title'] = response.css('title::text').get()

        # Extract description from <meta name="description">
        # Optimized description extraction: find meta tag with name="description"
        description_selector = response.css('meta[name="description"]::attr(content)')
        item['description'] = description_selector.get()

        # You can extend this to extract other meta tags or structured data (JSON-LD)
        # item['keywords_meta'] = response.css('meta[name="keywords"]::attr(content)').get()
        # item['og_title'] = response.css('meta[property="og:title"]::attr(content)').get()
        # ...

        # The item will now go through the pipeline for further processing
        yield item

        # In a real spider, you'd also extract links and yield new requests here
        # For recursive crawling (like for the eval set), a CrawlSpider with rules is better
        # next_pages = response.css('a::attr(href)').getall()
        # for next_page in next_pages:
        #     yield response.follow(next_page, self.parse)