# settings.py

BOT_NAME = "news_classifier_crawler"

SPIDER_MODULES = ["news_classifier_crawler.spiders"]
NEWSPIDER_MODULE = "news_classifier_crawler.spiders"

# Obey robots.txt rules - Set to False for evaluation crawling, but be mindful
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# Adjust based on your VM resources (2 vCPU, 4GB RAM) and website politeness
# Playwright is resource intensive. Start low, maybe 4-8, and increase cautiously.
CONCURRENT_REQUESTS = 8 # Increased from 1

# Set a real User-Agent - Good practice
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36' # Use a recent Chrome UA

# Configure a delay for requests for the same website (default: 0)
# IMPORTANT: DOWNLOAD_DELAY works *between* requests to the same domain *by Scrapy's core*.
# Playwright introduces its own browser context which might handle connections differently.
# If AUTOTHROTTLE is enabled, DOWNLOAD_DELAY is ignored. Let's disable AUTOTHROTTLE and set a base delay.
DOWNLOAD_DELAY = 1 # Be polite, wait 1 second between requests to the same domain (if not using Autothrottle)

# Disable AutoThrottle and HTTP Cache for simplicity during initial setup/debugging
# AUTOTHROTTLE_ENABLED = False # Keep enabled if you want dynamic delay
# AUTOTHROTTLE_START_DELAY = 3
# AUTOTHROTTLE_MAX_DELAY = 10
# HTTPCACHE_ENABLED = False

# Configure Download Handlers - Ensure Playwright handles http/https
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    # You can remove other default handlers if you are ONLY using http/https
}

# Playwright settings
PLAYWRIGHT_BROWSER_TYPE = "chromium" # 'chromium', 'firefox' or 'webkit'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True, # Run browser in headless mode (set to False for debugging)
    "timeout": 60000, # 60 seconds timeout for browser launch
    "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"], # Recommended args for Linux VMs
}
# Timeout for page navigation, including initial load and subsequent redirects/AJAX
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 90000 # 90 seconds
# Default state to wait for after navigation. 'networkidle' is often needed for dynamic sites.
# Consider 'domcontentloaded' or 'load' if networkidle is too slow/flaky.
PLAYWRIGHT_DEFAULT_LOAD_STATE = 'networkidle'

# --- Global Request Aborting with Playwright ---
# Specify a function that Playwright will use to decide whether to abort a request
PLAYWRIGHT_ABORT_REQUEST = 'news_classifier_crawler.settings.should_abort_request'

# Function to decide whether to abort a request in Playwright context
# This is MORE effective than Scrapy's allowed_domains for resources loaded by JS
def should_abort_request(request):
    # Abort requests for specific resource types (e.g., images, fonts, media)
    # if you don't need them for content extraction. This saves bandwidth and CPU.
    # Ensure 'document' is NOT in this list if you want to load the main page frame.
    aborted_resource_types = ["image", "font", "media", "stylesheet", "script", "xhr", "fetch", "websocket"]
    if request.resource_type in aborted_resource_types:
        return True

    # Abort requests to known advertisement, tracking, or unwanted domains
    # This list should be comprehensive based on observed requests in browser dev tools or logs
    unwanted_domains = [
        # Generic ad/tracking indicators
        'googleadservices.com', 'googlesyndication.com', 'doubleclick.net', 'adservice.', '.ads.', '/ads/',
        'rubiconproject.com', 'pubmatic.com', 'casalemedia.com', 'openx.net', 'adnxs.com', 'criteo.com',
        'indexww.com', 'bidswitch.net', 'simpli.fi', 'smartadserver.com', 'tapad.com', 'onetrust.com',
        'permutive.com', 'chartbeat.net', 'scorecardresearch.com', 'imrworldwide.com',
        'liadm.com', 'connatix.com', 'yieldmo.com', 'vrtcal.com', 'unruly.com', 'trustx.org',
        'dotomi.com', 'bluekai.com', 'demdex.net', 'evidon.com', 'quantserve.com', 'sharethrough.com',
        'zemanta.com', 'zyppah.com',
        # Specific examples from your list and common ones
        'piano.io', # The domain causing issues
        's.ad.smaato.net',
        'google-analytics.com', 'googletagmanager.com',
        'twitter.com', 'platform.twitter.com', # Twitter embeds
        'youtube.com', 'youtu.be', 'vimeo.com', 'jwplayer.com', # Video players/embeds
        'facebook.net', 'facebook.com', 'linkedin.com', 'pinterest.com', # Social media embeds/trackers
        'use.typekit.net', 'fonts.googleapis.com', 'fonts.gstatic.com', # Fonts
        'cdnjs.cloudflare.com', 'jsdelivr.net', 'code.jquery.com', # CDNs for common libraries
        'w.org', 'wp.com', # WordPress specific
        'google.com/recaptcha', 'www.recaptcha.net', # Captcha
        'cloudflare.com/cdn-cgi', # Cloudflare checks
        'microsoft.com', 'msn.com', 'bing.com', # Microsoft/Bing specific trackers (if not the target domain itself)
        'qq.com', 'gtimg.com', 'beacon.qq.com', 'trace.qq.com', 'qpic.cn', 'qimei.qq.com', # Tencent trackers
        # Add more based on your observation of blocked requests or network traffic
    ]
    # Convert request URL to lowercase for case-insensitive matching
    request_url_lower = request.url.lower()
    if any(domain in request_url_lower for domain in unwanted_domains):
        return True

    # Abort if the request URL pattern matches common API endpoints or unwanted paths
    unwanted_paths = [
        '/api/', '/ajax/', '/data/', '/json/', '/graphql', # API endpoints
        '/track', '/stats', '/pixel', '/beacon', '/log', # Tracking paths
        '/jwplayer/', '/vpaid/', '/vast/', # Video ad related paths
        '/optimizely/', '/launchdarkly/', '/googleoptimize/', # A/B testing
        '/consent/', '/cookie/', '/privacy/', # Consent popups related scripts (sometimes)
    ]
    if any(path in request_url_lower for path in unwanted_paths):
        return True

    # Do not abort the request by default
    return False


# Maximum number of concurrent pages Playwright will open
# Keep this reasonable based on your VM's memory (4GB). Each browser instance/page
# can consume significant RAM. Start with 4-8.
PLAYWRIGHT_MAX_PAGES = 8 # Was 20, reducing due to 4GB RAM

# Maximum requests per page (optional, can limit resources used by one page)
# PLAYWRIGHT_MAX_REQUESTS_PER_PAGE = 1000 # Example: a high limit to allow normal loading

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Enable or disable spider middlewares (default settings are usually fine)
# SPIDER_MIDDLEWARES = {
#    "news_classifier_crawler.middlewares.NewsClassifierCrawlerSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# Crucially, disable Scrapy's built-in filtering middlewares if you are
# relying on Playwright's handler and ALLOWED_DOMAINS is handled by LinkExtractor
# and Playwright's abort logic.
DOWNLOADER_MIDDLEWARES = {
    # 'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': None, # Explicitly disabled via ROBOTSTXT_OBEY=False
    'scrapy.downloadermiddlewares.offsite.OffsiteMiddleware': None,   # Disable - Playwright/LinkExtractor handles this
    # 'scrapy.downloadermiddlewares.dupefilter.DupeFilter': None,       # Disable default DupeFilter if using custom logic or relying on Playwright
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None, # Can disable if USER_AGENT is set
    # Add your custom middlewares if any
    # 'scrapy_playwright.middleware.PlaywrightMiddleware': 725, # New versions integrate into handler
}
# Note: PlaywrightDownloadHandler handles the interaction with the browser.
# Most Scrapy middlewares run *before* the handler sends the request to Playwright,
# or *after* the handler returns the response. Be mindful of their order and effect.

# Enable or disable extensions
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# The order matters (lower number runs first)
ITEM_PIPELINES = {
   "news_classifier_crawler.pipelines.ContentExtractionPipeline": 300, # Your custom pipeline for Trafilatura/spaCy
   # Add other pipelines if needed (e.g., for validation, database storage)
   # "news_classifier_crawler.pipelines.ValidateItemPipeline": 310,
   # "news_classifier_crawler.pipelines.DatabaseStoragePipeline": 400,
}

# Configure Asyncio reactor (required by scrapy-playwright)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Configure logging level (DEBUG for development, INFO for production)
LOG_LEVEL = 'DEBUG' # 'INFO', 'WARNING', 'ERROR'
# LOG_FILE = 'scrapy.log' # Optional: write logs to a file

# Output settings
# FEED_FORMAT = 'jsonlines' # Output format (e.g., json, jsonlines, csv, xml)
# FEED_URI = 'crawled_data.jsonl' # Output file path

# Ensure that DOWNLOAD_HANDLERS are correctly merged if you have other handlers defined elsewhere
# If you only use http/https with Playwright, the current DOWNLOAD_HANDLERS is sufficient.
# If you need to keep other handlers (e.g., for file://), you might need to
# handle the merging logic carefully, but often just defining http/https with Playwright is enough.