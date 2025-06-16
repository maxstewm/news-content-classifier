import scrapy
from scrapy.linkextractors import LinkExtractor
# Note: We might not need CrawlSpider anymore, but let's keep it for now and just comment out the rules
# from scrapy.spiders import CrawlSpider, Rule
from scrapy import Spider # Corrected import for the base Spider class
from news_classifier_crawler.items import NewsArticleItem
from urllib.parse import urlparse
import logging
from scrapy_playwright.page import PageMethod
import asyncio

# Set up logging for the spider
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG) # Can configure in settings.py

# Change the base class from CrawlSpider to Spider
class EvaluationSpider(Spider): # Changed from CrawlSpider
    name = "eval_spider"

    # Define the 20 core domains for evaluation - IMPORTANT: Replace with your actual 20 domains
    # Add common subdomains for your target sites
    core_domains = [
        "npr.org",
        "bleacherreport.com",
        "variety.com",
        "hollywoodreporter.com",
        "webmd.com",
        "statnews.com",
        "politico.com",
        "cnn.com", # Keep the base domain
        "edition.cnn.com", # Add CNN's specific content subdomain
        # "msn.com", # COMMENTED OUT - Failed to load
        # "foxnews.com", # Add if you intend to crawl it and it's in start_urls
        "sciencedaily.com", # Added back
        # ... Add/Verify other core domains ...
    ]
    # allowed_domains is still useful for Scrapy's OffsiteMiddleware if it were enabled,
    # but we primarily rely on LinkExtractor's allow_domains and our manual check.
    allowed_domains = core_domains

    # 初始请求列表 - 用于启动爬虫
    # 请确保这里的 URL 是有效的，且能从这些页面提取到文章链接
    # 建议使用 https 协议
    start_urls = [f"https://www.{domain}" for domain in core_domains if domain not in ["amazon.com", "msn.com", "edition.cnn.com", "sciencedaily.com"]] # Exclude some known problem domains or those with specific subdomains
    # Manually add specific start URLs that might redirect or are not www., or specific entry points
    start_urls.extend([
        "https://edition.cnn.com/", # Use the actual landing page for CNN
        "https://www.npr.org/sections/news/",
        # "https://www.cnn.com/world", # Keep if you want this as a starting point
        "https://www.foxnews.com/politics", # Keep if foxnews.com is in core_domains
        "https://www.sciencedaily.com/news/", # Specific news section for ScienceDaily
        # "https://www.bleacherreport.com/nba", # Example specific section
        # "https://www.variety.com/category/news/", # Example specific section
        # "https://www.webmd.com/news/", # Example specific section
        # "https://www.politico.com/news/", # Example specific section
        # "https://liliputing.com/", # Example specific section
        # Add your core domain's specific news/article list page URLs
    ])


    # Counter to limit pages per domain
    crawled_count_per_domain = {}
    page_limit_per_domain = 100 # Target 100 pages per domain

    # Playwright configuration template (used when yielding Requests)
    PLAYWRIGHT_META_TEMPLATE = {
        "playwright": True,
        # "playwright_include_page": True, # Uncomment if you need to manually interact with 'page' object in callback
        "playwright_page_methods": [
            # Wait for network to be idle, good for dynamic content
             PageMethod('wait_for_load_state', 'networkidle'),
            # Alternatively, wait for a specific selector if you know one appears when content is loaded
            # PageMethod('wait_for_selector', 'body') # Example: PageMethod('wait_for_selector', 'div.main-content-area')
        ],
        # We will use the global PLAYWRIGHT_ABORT_REQUEST setting defined in settings.py for routing
        # "playwright_route" can also be defined here if needed per request
    }

    # Link Extractor instance defined here using the class attributes
    link_extractor = LinkExtractor(
         allow_domains=allowed_domains, # Limit to ALL allowed domains (including subdomains)
         allow=( # Regex patterns for URLs we want to follow (both list/index pages AND potential article pages)
             # --- General Patterns (often good candidates for articles) ---
             r'/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/]+/$', # YYYY/MM/DD/slug/ (with slash)
             r'/[0-9]{4}/[0-9]{2}/[^/]+/$', # YYYY/MM/slug/ (with slash)
             r'/article/',
             r'/story/',
             r'/news/',
             r'/vip/', # variety.com example
             r'/20[0-9]{2}/', # Links containing a year

             # --- More specific patterns based on observed links (adjust/add as needed) ---
             r'/\w+/\d{4}/\d{2}/\d{2}/.+?/$', # Category/YYYY/MM/DD/slug/ (with slash)
             r'/\d{4}/\d{2}/\d{2}/.+?\.html$', # YYYY/MM/DD/slug.html (ends with .html)
             r'/[^/]+/(\d+)/?$', # E.g., category/id or slug/id (use with caution)
             r'/([a-zA-Z0-9-]+)/story/([a-zA-Z0-9-]+)', # Generic category/story pattern
             r'/[a-zA-Z0-9-]+-\d+$', # slug-ID pattern (e.g., politico)

             # CNN specific patterns based on log:
             # r'/election/2025$', # Matches Link 1 - seems like a section, maybe deny this unless you need it?
             r'/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/]+$', # CNN article pattern from your log (NO trailing slash)
             r'/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/]+-intl(?:-hnk|-latam)?$', # CNN international/other suffixes (NO trailing slash)
             r'/[a-zA-Z-]+/\d{4}/\d{2}/\d{2}/[^/]+$', # e.g., /politics/2025/05/14/... (NO trailing slash)

             # Politico specific pattern from log:
             r'/news/\d{4}/\d{2}/\d{2}/[^/]+-\d+$', # /news/YYYY/MM/DD/slug-ID

             # NPR specific pattern (based on observed URLs):
             r'/\d{4}/\d{2}/\d{2}/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+$', # YYYY/MM/DD/segment/slug (e.g. /2025/05/15/123456789/slug)
             r'/\d{4}/\d{2}/\d{2}/nx-s1-\d+/', # NPR specific pattern from your original start_urls

             # ScienceDaily specific pattern (based on observed URLs):
             r'/releases/\d{4}/[0-9]{2}/\d{6}\.htm$', # /releases/YYYY/MM/DDDDDD.htm

             # Add patterns for Bleacher Report, Variety, Hollywood Reporter, WebMD, Stat News etc.
             r'/([a-zA-Z-]+)/\d{4}/\d{2}/\d{2}/.+?$', # Generic category/date/slug (no trailing slash)
             r'/[a-zA-Z-]+/\d{4}/\d{2}/.+?$', # Generic category/year/month/slug (no trailing slash)


             # --- Patterns for list/index pages (if they are entry points to more links) ---
             r'/sections/\w+/?$', # NPR sections (list pages, optional trailing slash)
             r'/category/[^/]+/?$', # Category pages (list pages)
             r'/page/\d+/?$', # Pagination

         ),
         deny=(
             r'/author/', r'/tag/', r'/about/', r'/contact/', r'/careers/', r'/shop/', r'/subscribe/',
             r'/login/', r'/register/', r'/privacy/', r'/terms/', r'/sitemap\.xml$',
             r'\.(pdf|jpg|png|gif|css|js)$', # Files - simplified regex
             r'/videos/', r'/photos/', r'/gallery/',
             r'#',
             r'/index\.html$', r'/default\.htm$',
             r'/\d+/$', # Avoid simple numeric paths

             # Deny root domains to avoid re-crawling homepages constantly unless explicitly allowed above
             # This regex denies URLs that are exactly the root domain followed by an optional slash
             r'^https://(www\.)?(' + '|'.join([d.replace('.', '\.') for d in core_domains]) + ')/?$',
             # Deny specific sections that are not articles, e.g., CNN election page if not needed
             # r'/election/\d+/?$', # Example deny rule


             # Add patterns for common site features you don't want to crawl
             r'/press-release/', r'/sponsored/', r'/partners/', r'/membership/', r'/newsletter/', r'/feedback/',
             r'/api/', r'/ajax/', r'/data/', r'/json/', r'/graphql',

             # Add more based on observed URLs you don't want to crawl
         ),
         # --- Temporarily remove restrict_css for debugging! ---
         # restrict_css=(
         #     'div.stream-item', # Common for article list items
         #     'div.card', # Another common pattern for article cards
         #     'article', # HTML5 article tag often contains links
         #     'div[data-module="content-card"]', # CNN example
         #     'div.river--inner > div.item', # Politico example (inspect HTML)
         #     'main a', # Links within the main content area
         #     # Add selectors relevant to your target sites' article lists/main content areas
         # ),
         # process_links=self.process_extracted_links # Optional: add a method to filter/modify links after extraction
    )

    # --- COMMENT OUT or REMOVE the rules tuple ---
    # rules = (
    #     Rule(
    #         link_extractor=link_extractor,
    #         callback='parse_page',
    #         follow=True,
    #         process_request='process_rule_request' # This method is now unused
    #     ),
    # )

    # --- REMOVE the process_rule_request method ---
    # def process_rule_request(self, request, response):
    #     # This method is no longer used with manual link extraction
    #     pass # Or remove the method entirely


    def __init__(self, *args, **kwargs):
        super(EvaluationSpider, self).__init__(*args, **kwargs)
        # Initialize the counter for all domains in core_domains
        for domain in self.core_domains:
            self.crawled_count_per_domain[domain] = 0
        self.logger.info(f"Evaluation spider started. Target {self.page_limit_per_domain} pages per domain.")
        self.logger.info(f"Initial start_urls: {self.start_urls}")


    def start_requests(self):
        # Override start_requests to add Playwright meta to the initial requests
        self.logger.info("Generating start requests with Playwright meta.")
        for url in self.start_urls:
             # Ensure URL is within allowed_domains before starting
             try:
                 parsed_url = urlparse(url)
                 domain = parsed_url.netloc.replace("www.", "")
                 # Check if domain is in allowed_domains OR if it's a redirect target of one
                 # For simplicity, we'll just check if the parsed domain is in allowed_domains
                 if domain not in self.allowed_domains:
                      self.logger.warning(f"Skipping start_url outside allowed_domains: {url} (Parsed domain: {domain})")
                      continue # Skip this URL if it's not in allowed domains
             except Exception as e:
                 self.logger.error(f"Failed to parse URL {url} in start_requests: {e}")
                 continue


             self.logger.info(f"Yielding Playwright start request for URL: {url}")
             # Add the core domain key to meta
             meta_with_domain = self.PLAYWRIGHT_META_TEMPLATE.copy() # Create a copy to avoid modifying the template
             # Use the domain derived from the original start URL for counting purposes
             meta_with_domain['core_domain_key'] = domain
             # You can add playwright_route here if needed, but global abort in settings is often sufficient

             yield scrapy.Request(
                 url=url,
                 meta=meta_with_domain, # Apply Playwright and domain meta
                 callback=self.parse_page, # Initial pages go to parse_page
                 errback=self.on_playwright_error, # Handle Playwright errors
                 priority=100 # High priority for start requests
             )


    # Add this new error handling method
    async def on_playwright_error(self, failure):
         # This method is called when a Playwright request fails (e.g., timeout, browser error)
         request = failure.request # Get the failed request object
         error_message = failure.getErrorMessage() # Get the error message
         self.logger.error(f"Playwright Request failed for {request.url}: {error_message}")
         # Optional: You could yield an item here to log the failure or retry
         # For now, just log the error.


    async def parse_page(self, response):
        # This method receives the response *after* Playwright rendering
        # It handles both potential article pages and index/list pages

        url = response.url
        status = response.status
        # Get the domain key from meta (added in start_requests or process_rule_request)
        current_domain = response.meta.get('core_domain_key')
        # It's possible a link to an allowed domain was found on a page *not* in core_domains.
        # In that case, core_domain_key might be None. Let's re-parse the response URL's domain
        # but use the meta key if available as it reflects the *intended* target domain from the rule/start.
        if not current_domain:
             # Fallback if core_domain_key was not set for some reason
             current_domain = urlparse(url).netloc.replace("www.", "")
             self.logger.warning(f"DEBUG: core_domain_key missing in meta for {url}. Using parsed domain: {current_domain}. Ensure meta is passed correctly.")


        self.logger.debug(f">>> Processing page {url} (Domain: {current_domain}, Status: {status})")


        if status != 200:
            self.logger.error(f"Failed to load page: {url} with status {status}")
            # Important: If playwright_include_page was True, close the page here
            # (Note: We removed playwright_include_page from the template, so this might not be needed)
            if response.meta.get("playwright_include_page"):
                 try:
                     page = response.meta["playwright_page"]
                     await page.close()
                     self.logger.debug(f"Closed Playwright page for failed request {url}")
                 except Exception as e:
                      self.logger.error(f"Error closing Playwright page for failed request {url}: {e}")
            return

        # Check if it's a core domain and hasn't reached the limit
        # Use the current_domain (derived from meta or response URL) for counting
        is_core_domain = current_domain in self.core_domains # Check if the page's domain is in the core list
        domain_count = self.crawled_count_per_domain.get(current_domain, 0)
        should_process_item = is_core_domain and domain_count < self.page_limit_per_domain

        if should_process_item:
            # --- Create and Yield Item ---
            # Increment count *before* yielding item
            self.crawled_count_per_domain[current_domain] = domain_count + 1
            self.logger.info(f"[{current_domain}] COUNT: {self.crawled_count_per_domain[current_domain]}/{self.page_limit_per_domain}. Yielding ITEM for {url}")

            item = NewsArticleItem()
            item['url'] = url
            # Store rendered HTML for the pipeline
            item['rendered_html'] = response.text

            # --- Extract basic metadata using Scrapy Selectors ---
            # Use common selectors, refine based on your core domains if needed
            item['title'] = response.css('head title::text').get() or response.css('h1::text').get()
            # Attempt to get description from meta tags, common ones are 'description' or 'og:description'
            item['description'] = response.css('meta[name="description"]::attr(content)').get() or \
                                 response.css('meta[property="og:description"]::attr(content)').get() or \
                                 "" # Default to empty string if not found

            # Yield the item. It will go through the pipeline(s).
            yield item

            # Note: Link extraction and follow is now handled *manually* below

        elif is_core_domain and domain_count >= self.page_limit_per_domain:
             self.logger.info(f"[{current_domain}] Domain limit {self.page_limit_per_domain} reached. Skipping ITEM yield and further link extraction from {url}")
             # If domain limit reached, stop extracting/yielding further links from this page for this domain
             return # Stop processing this page further for this domain


        # --- Manual Link Extraction and Yielding for Following ---
        # Only extract/yield links if we haven't reached the domain limit for the current page's domain
        # OR if the page's domain is not one of the core domains (we still want to follow links *from* these pages if they lead to core domains)
        if not is_core_domain or domain_count < self.page_limit_per_domain:
             self.logger.debug(f"DEBUG: --- Manually extracting and yielding links from {url} ---")
             le = self.link_extractor # Use the spider's pre-configured instance
             # LinkExtractor automatically applies allow_domains, allow, deny, restrict_css
             links_to_follow = le.extract_links(response)

             self.logger.debug(f"DEBUG: LinkExtractor found {len(links_to_follow)} valid links to follow on {url}.")

             # Prepare Playwright meta template for next requests
             next_request_meta_template = self.PLAYWRIGHT_META_TEMPLATE.copy()

             for i, link in enumerate(links_to_follow):
                 try:
                     # Re-check domain just for safety and to get the correct core_domain_key
                     parsed_link_url = urlparse(link.url)
                     link_domain = parsed_link_url.netloc.replace("www.", "")

                     # Although LinkExtractor with allow_domains should handle this,
                     # we explicitly check again before yielding to be absolutely sure
                     # and to assign the correct core_domain_key for the *next* request's processing
                     if link_domain in self.core_domains:
                          # Add the domain key to the meta for the next request
                          next_request_meta = next_request_meta_template.copy() # Copy again for each request
                          next_request_meta['core_domain_key'] = link_domain

                          self.logger.debug(f"DEBUG: Manually yielding Request {i+1} for: {link.url}")
                          yield scrapy.Request(
                              url=link.url,
                              callback=self.parse_page, # Send to the same parser for extraction AND further link finding
                              meta=next_request_meta, # Apply Playwright and domain meta
                              errback=self.on_playwright_error,
                              priority=10 # Lower priority than start_urls, higher than default
                          )
                     else:
                          # This case should not happen if LinkExtractor's allow_domains is set correctly
                          self.logger.debug(f"DEBUG: Manually skipping link outside core_domains (should be filtered by LinkExtractor): {link.url}")

                 except Exception as e:
                      self.logger.error(f"DEBUG: !!! An ERROR occurred processing extracted link {link.url} manually: {e}")

             self.logger.debug(f"DEBUG: --- Finished manual link yielding from {url} ---")

        else:
             # Page is a core domain page, but domain limit was reached, links are not extracted/followed from this page
             self.logger.debug(f"DEBUG: Skipping link extraction from {url} as domain limit reached for {current_domain}.")


        # Ensure the page is closed if playwright_include_page was True (it's False by default in template now)
        # This block might not be necessary anymore unless you explicitly set playwright_include_page = True
        if response.meta.get("playwright_include_page"):
             try:
                 page = response.meta["playwright_page"]
                 await page.close()
                 self.logger.debug(f"Closed Playwright page for {url}")
             except Exception as e:
                 self.logger.error(f"Error closing Playwright page for {url}: {e}")


    # Optional: Override closed method to report final counts
    def closed(self, reason):
        self.logger.info("Spider closed. Final counts per domain:")
        for domain in self.core_domains:
             count = self.crawled_count_per_domain.get(domain, 0)
             self.logger.info(f"  {domain}: {count} pages")
        self.logger.info(f"Spider closed reason: {reason}")