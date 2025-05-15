# settings.py

# ... other settings ...

BOT_NAME = "news_classifier_crawler"
SPIDER_MODULES = ["news_classifier_crawler.spiders"]
NEWSPIDER_MODULE = "news_classifier_crawler.spiders"

ROBOTSTXT_OBEY = False # 先保留 Robots.txt 遵守

DOWNLOAD_DELAY = 1 # 可以调小一点，因为只抓一个页面

# !!! 暂时注释掉 Playwright 的下载处理器 !!!
DOWNLOAD_HANDLERS = {
    # "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    # "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# !!! 暂时注释掉 Playwright 中间件 (虽然您之前已经移除了 DOWNLOADER_MIDDLEWARES 整个块，但确保 Playwright 的中间件没有在其他地方被启用)
# DOWNLOADER_MIDDLEWARES = {
#    "scrapy_playwright.middleware.PlaywrightMiddleware": 725,
# }


# !!! 暂时注释掉您的内容提取 Pipeline !!!
ITEM_PIPELINES = {
   # "news_classifier_crawler.pipelines.ContentExtractionPipeline": 300,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor" # 这个可以保留

# ... rest of your settings ...

# Output format - configure this later to export as JSON Lines for Label Studio
FEED_FORMAT = 'jsonlines'
#FEED_URI = 'crawled_data.jsonl'