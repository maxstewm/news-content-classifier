# settings.py

BOT_NAME = "news_classifier_crawler"

SPIDER_MODULES = ["news_classifier_crawler.spiders"]
NEWSPIDER_MODULE = "news_classifier_crawler.spiders"

# Obey robots.txt rules - IMPORTANT for ethical crawling
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2 # Be polite, wait 2 seconds between requests to the same domain
# The download delay setting will only work when AUTO_THROTTLE is disabled.

#DOWNLOAD_HANDLERS_BASE = {
    # 这里列出 Scrapy 默认的 handler，Playwright 会覆盖 http/https
    # 默认 handlers 可以参考 scrapy 官方文档，或者不设置这个，让 Scrapy 自己合并
#}

#simple_spider设置
DOWNLOAD_HANDLERS_BASE = None

# Explicitly list the download handlers and their order
DOWNLOAD_HANDLERS = {
    #"http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    #"https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    # 保留其他可能的 handler，例如 file:// 等，但确保 http/https 是 Playwright
    # "file": "scrapy.core.downloader.handlers.file.FileDownloadHandler",
    # "s3": "scrapy.core.downloader.handlers.s3.S3DownloadHandler",
}

# Playwright settings
PLAYWRIGHT_BROWSER_TYPE = "chromium" # 'chromium', 'firefox' or 'webkit'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True, # Run browser in headless mode
    "timeout": 90000, # 20 seconds timeout
    # Optional: Add args that might help with stability
    "args": ["--no-sandbox", "--disable-setuid-sandbox"], # 有时在Linux容器环境有用
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 90000 # 30 seconds timeout for page navigation
PLAYWRIGHT_DEFAULT_LOAD_STATE = 'domcontentloaded' # !!! 添加或修改这行 !!!

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
   #"news_classifier_crawler.pipelines.ContentExtractionPipeline": 300, # Your custom pipeline
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
LOG_LEVEL = 'DEBUG'