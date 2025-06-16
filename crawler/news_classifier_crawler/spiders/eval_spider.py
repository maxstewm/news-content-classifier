import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy import Spider
from news_classifier_crawler.items import NewsArticleItem
from urllib.parse import urlparse, urljoin
import logging
from scrapy_playwright.page import PageMethod
import asyncio
from datetime import datetime
import re
# Crawler import is no longer needed if from_crawler is removed or simplified
# from scrapy.crawler import Crawler
class EvaluationSpider(Spider):
    name = "eval_spider"

    # Define the 20 core domains for evaluation - IMPORTANT: Replace with your actual 20 domains
    # Add common subdomains for your target sites
    core_domains = [
        #"npr.org",
        #"bleacherreport.com",
        #"variety.com",
        #"hollywoodreporter.com",
        #"webmd.com",
        #"statnews.com",
        #"politico.com",
        #"cnn.com", # Keep the base domain
        #"edition.cnn.com", # Add CNN's specific content subdomain
         "msn.com", # Temporarily removed due to ERR_FAILED
        # "foxnews.com", # Temporarily removed due to 403 Forbidden
        # "sciencedaily.com", # Temporarily removed if it has CAPTCHA issues
        # ... Add/Verify other core domains and their subdomains ...
    ]
    # allowed_domains is still useful for Scrapy's OffsiteMiddleware if it were enabled,
    # but we primarily rely on LinkExtractor's allow_domains and our manual check.
    allowed_domains = core_domains

    # 初始请求列表 - 用于启动爬虫
    # 请确保这里的 URL 是有效的，且能从这些页面提取到文章链接
    # 建议使用 https 协议
    start_urls = [f"https://www.{domain}" for domain in core_domains if domain not in ["amazon.com",  "edition.cnn.com", "sciencedaily.com"]] # Exclude some known problem domains or those with specific subdomains
    # Manually add specific start URLs that might redirect or are not www., or specific entry points
    start_urls.extend([
        # MSN Specific Start URLs - Use News/Sport/Category List Pages
        #"https://www.msn.com/en-sg/news", # Example News list page
        "https://www.msn.com/en-sg/sport", # Example Sport list page
        "https://www.msn.com/en-sg/money", # Example Money list page
        #"https://www.msn.com/en-us/money/savingandinvesting/popular-american-gym-chain-files-for-bankruptcy/ss-AA1EBmGO?ocid=hpmsn&cvid=3435b002656c4316c1a201983603a4fd&ei=10"
        #"https://edition.cnn.com/", # Use the actual landing page for CNN
        #"https://www.npr.org/sections/news/",
        #"https://www.cnn.com/world", # Keep if you want this as a starting point
        #"https://www.foxnews.com/politics", # 反爬厉害，Keep if foxnews.com is in core_domains
        #"https://www.sciencedaily.com/news/", # 需要人工验证，Specific news section for ScienceDaily
        #"https://www.bleacherreport.com/nba", # Example specific section
        #"https://www.variety.com/category/news/", # Example specific section
        #"https://www.webmd.com/news/", # Example specific section
        #"https://www.politico.com/news/", # Example specific section
        #"https://liliputing.com/", # Example specific section
        # Add your core domain's specific news/article list page URLs
    ])


    # Counter to limit pages per domain
    crawled_count_per_domain = {}
    page_limit_per_domain = 100 # Target 100 pages per domain

    # Store original allow/deny patterns to check URL patterns later
    _allow_patterns = ( # Store the original tuple here
             # --- General Article Patterns ---
             r'/[0-9]{4}/[0-9]{2}/[0-9]{2}/[^/]+/?$',
             r'/article/', r'/story/', r'/news/', r'/vip/', r'/20[0-9]{2}/',
             r'/\w+/\d{4}/\d{2}/\d{2}/.+?/?$', r'/\d{4}/\d{2}/\d{2}/.+?\.html$',
             r'/[^/]+/(\d+)/?$', r'/([a-zA-Z0-9-]+)/story/([a-zA-Z0-9-]+)',
             r'/[a-zA-Z0-9-]+-\d+$', # Politico example

             # --- MSN Specific Patterns ---
             r'/en-\w{2}/(?:[^/]+/)+[^/]+/ar-[a-zA-Z0-9]+/?', # Matches /en-xx/one/or/more/segments/slug/ar-ID
             r'/en-\w{2}/(?:[^/]+/)+[^/]+/ss-[a-zA-Z0-9]+/?', # Matches /en-xx/one/or/more/segments/slug/ss-ID

             # --- Patterns for List/Index/Pagination Pages (essential for recursive crawling) ---
             r'/sections/\w+/?$', r'/category/[^/]+/?$', r'/page/\d+/?$',
             r'/en-\w{2}/news/?$', r'/en-\w{2}/sport/?$', r'/en-\w{2}/money/?$',
             r'/en-\w{2}/[^/]+/?$', # More general pattern for category list pages

             # Add patterns for other core domains' list/article pages
         )
    _deny_patterns = ( # Store the original tuple here
             r'/author/', r'/tag/', r'/about/', r'/contact/', r'/careers/', r'/shop/', r'/subscribe/',
             r'/login/', r'/register/', r'/privacy/', r'/terms/', r'/sitemap\.xml$',
             r'\.(pdf|jpg|png|gif|css|js)$', # Files
             r'/videos/', r'/photos/', r'/gallery/', r'#',
             r'/index\.html$', r'/default\.htm$', r'/\d+/$',
             r'/live-updates/', r'/scoreboard/', r'/rankings/', r'/teams/', r'/players/', r'/stats/', r'/standings/',
             r'/draft/', r'/free-agency/', r'/trades/', r'/podcasts/', r'/audio/',
             r'/press-release/', r'/sponsored/', r'/partners/', r'/membership/', r'/newsletter/', r'/feedback/',
             r'/api/', r'/ajax/', r'/data/', r'/json/', r'/graphql',
             r'/cdn-cgi/', r'/cloudflare-static/', r'/app/', r'/cdn/', r'/static/', r'/assets/',

             # --- MSN Specific Deny Patterns (if any) ---
             r'/en-\w{2}/weather/?$', r'/en-\w{2}/travel/?$', r'/en-\w{2}/lifestyle/?$',
             r'/en-\w{2}/bing-maps/?$', r'/en-\w{2}/weather/?$', r'/en-\w{2}/travel/?$', r'/en-\w{2}/shopping/?$',
             r'/en-\w{2}/how-to/?$', r'/en-\w{2}/autos/?$', r'/en-\w{2}/foodanddrink/?$', r'/en-\w{2}/bing-chat/?$',
         )


    # Link Extractor instance defined here - uses the _allow_patterns and _deny_patterns
    link_extractor = LinkExtractor(
         allow_domains=allowed_domains,
         allow=_allow_patterns, # Use the stored tuple
         deny=_deny_patterns,   # Use the stored tuple
         # --- Add restrict_css for list pages! ---
         # Inspect MSN News/Sport/Money pages (RENDERED HTML) to find the CSS selectors
         restrict_css=(
             'div.grid-view-feed-root', # The main grid container
             'div.feed', # Inner feed container
             'cs-responsive-card', # The article card itself
             'social-bar-wc', # The social bar within the card
             # Add selectors relevant to other target sites' article lists
             'div.stream-item', 'div.card', 'main', 'section', 'ul.list-news',
         ),
         # process_links=self.process_extracted_links # Optional
    )


    # Playwright configuration template
    PLAYWRIGHT_META_TEMPLATE = {
    "playwright": True,
    "playwright_page_methods": [
         # Try waiting for the main feed container to appear
         # Replace with the actual selector you find
         PageMethod('wait_for_selector', 'div[role="main"].grid-view-feed-root'),
         PageMethod('wait_for_timeout', 5000), # Keep a small timeout after selector appears just in case
         # PageMethod('wait_for_load_state', 'networkidle'), # You can keep or remove networkidle
    ],
    "playwright_navigation_timeout": 180000,
     "playwright_include_page": True, # Keep this False unless you need page object for scrolling etc.
}


    # --- REMOVED DupeFilter instance variable and from_crawler method ---
    # dupefilter = None # Removed
    # @classmethod # Removed
    # def from_crawler(cls, crawler: Crawler, *args, **kwargs): # Removed
    #    # ... (DupeFilter access logic removed) ...
    #    return spider # Removed


    # --- __init__ method - Keep simple initialization ---
    def __init__(self, *args, **kwargs):
        super(EvaluationSpider, self).__init__(*args, **kwargs)
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

             meta_with_domain = self.PLAYWRIGHT_META_TEMPLATE.copy() # Create a copy to avoid modifying the template
             # Use the domain derived from the original start URL for counting purposes
             meta_with_domain['core_domain_key'] = domain
             meta_with_domain['is_start_request'] = True # Mark as start request if needed later


             # --- Apply domain-specific Playwright meta overrides ---
             # Note: The default template uses 'networkidle'. Let's stick to that
             # unless 'domcontentloaded' specifically fixed the initial load.
             # If networkidle caused timeouts on other sites, you might need domain-specific waits here.
             if domain == "msn.com":
                 self.logger.info(f"Applying specific Playwright meta for MSN: {url}")
                 meta_with_domain["playwright_page_methods"] = [
                     # Try networkidle first, add fixed wait
                     PageMethod('wait_for_load_state', 'networkidle'),
                     PageMethod('wait_for_timeout', 10000), # Add a fixed wait after load state for JS to render content
                 ]
                 meta_with_domain["playwright_navigation_timeout"] = 180000 # Increase timeout to 180 seconds

             # --- Specific overrides for ScienceDaily if kept ---
             if domain == "sciencedaily.com":
                  self.logger.info(f"Applying specific Playwright meta for ScienceDaily: {url}")
                  meta_with_domain["playwright_page_methods"] = [
                       PageMethod('wait_for_load_state', 'domcontentloaded'),
                       PageMethod('wait_for_timeout', 5000),
                       # Add wait_for_selector if a specific element indicates content load after challenge
                       # PageMethod('wait_for_selector', 'div#main-content'), # Example selector
                  ]
                  meta_with_domain["playwright_navigation_timeout"] = 180000

             # --- Specific overrides for FoxNews if kept ---
             if domain == "foxnews.com":
                  self.logger.info(f"Applying specific Playwright meta for FoxNews: {url}")
                  meta_with_domain["playwright_page_methods"] = [
                       PageMethod('wait_for_load_state', 'domcontentloaded'), # Try faster load state
                       PageMethod('wait_for_timeout', 3000), # Short fixed wait
                       # Add wait_for_selector for a key content element if needed
                       # PageMethod('wait_for_selector', '.article-body'), # Example selector
                  ]
                  meta_with_domain["playwright_navigation_timeout"] = 120000 # Increase timeout

             # Add other domain-specific overrides here


             yield scrapy.Request(
                 url=url,
                 meta=meta_with_domain, # Apply Playwright and domain meta
                 callback=self.parse_page, # Initial pages go to parse_page
                 errback=self.on_playwright_error, # Handle Playwright errors
                 priority=100 # High priority for start requests
             )


    # Add this new error handling method
    async def on_playwright_error(self, failure):
         # This method is called when a Playwright request fails (e.g., timeout, browser error, DNS error)
         request = failure.request # Get the failed request object
         error_message = failure.getErrorMessage() # Get the error message
         self.logger.error(f"Playwright Request failed for {request.url}: {error_message}")
         # Optional: You could yield an item here to log the failure or retry
         # For now, just log the error.


    # Helper function to safely extract text or attribute using CSS selector
    def safe_css(self, response, selector):
        """Extract text or attribute using CSS selector, return None or empty string if not found/error."""
        try:
            # Check if it's an attribute extraction (contains ::attr())
            if '::attr(' in selector:
                # Extract attribute name
                parts = selector.split('::attr(')
                css_part = parts[0]
                attr_part = parts[1].rstrip(')')
                result = response.css(css_part).attrib.get(attr_part)
            else:
                # Extract text
                result = response.css(selector).get()

            return result.strip() if result else "" # Return stripped string or empty

        except Exception as e:
            self.logger.warning(f"Failed to extract using selector '{selector}': {e}")
            return "" # Return empty string on error


    # Helper function to parse dates from various formats
    def parse_date(self, date_string):
         """Attempt to parse a date string into a standard format."""
         if not date_string:
              return None

         # Common date formats to try (add more based on observed sites)
         formats_to_try = [
             '%Y-%m-%dT%H:%M:%S%z', # ISO 8601 with timezone (e.g., 2023-10-27T10:00:00-05:00)
             '%Y-%m-%dT%H:%M:%S',   # ISO 8601 without timezone
             '%B %d, %Y',           # Full Month Name Day, Year (e.g., May 15, 2025)
             '%b %d, %Y',           # Abbreviated Month Name Day, Year (e.g., May 15, 2025)
             '%Y/%m/%d',           # YYYY/MM/DD
             '%m/%d/%Y',           # MM/DD/YYYY
             '%Y-%m-%d',           # YYYY-MM-DD
             # Add more formats as needed
         ]

         for fmt in formats_to_try:
             try:
                 dt_obj = datetime.strptime(date_string, fmt)
                 return dt_obj.isoformat() # Return in standard ISO format
             except ValueError:
                 pass # Try the next format

         # If no format matched, try parsing using dateutil (requires `pip install python-dateutil`)
         # from dateutil import parser as dateparser
         # try:
         #      dt_obj = dateparser.parse(date_string)
         #      return dt_obj.isoformat()
         # except (ValueError, TypeError):
         #      pass # dateutil failed

         self.logger.debug(f"Failed to parse date: {date_string}")
         return None # Return None if parsing fails

    async def parse_page(self, response):
        url = response.url
        status = response.status
        # Get the domain key from meta (added in start_requests or manual yield)
        current_domain = response.meta.get('core_domain_key')
        # It's possible a link to an allowed domain was found on a page *not* in core_domains.
        # In that case, core_domain_key might be None. Let's re-parse the response URL's domain
        # but use the meta key if available as it reflects the *intended* target domain from the rule/start.
        if not current_domain:
             # Fallback if core_domain_key was not set for some reason (shouldn't happen with manual yield now)
             current_domain = urlparse(url).netloc.replace("www.", "")
             self.logger.warning(f"DEBUG: core_domain_key missing in meta for {url}. Using parsed domain: {current_domain}. Ensure meta is passed correctly.")


        self.logger.debug(f">>> Processing page {url} (Domain: {current_domain}, Status: {status})")


         # --- Handle Non-200 Status Codes ---
        if status != 200:
             self.logger.error(f"Failed/Skipping processing for page: {url} with status {status}")
             if response.meta.get("playwright_include_page"):
                  try:
                      page = response.meta["playwright_page"]
                      await page.close()
                      self.logger.debug(f"Closed Playwright page for status {status} request {url}")
                  except Exception as e:
                       self.logger.error(f"Error closing Playwright page for status {status} request {url}: {e}")
             return


        # --- Determine if it's a likely article page to Yield Item ---
        is_likely_article_page = False

        # Use selectors to check for article content indicators (more reliable than URL alone)
        # Adjust these selectors based on inspection of RENDERED article pages for ALL your domains
        # Add more generic or site-specific selectors here
        if response.css('h1.main-title').get() or response.css('.article-content').get() or response.css('article.page-article').get() or response.css('div[itemprop="articleBody"]').get() or response.css('#story-body').get() or response.css('div.main article').get():
             is_likely_article_page = True
             self.logger.debug(f"DEBUG: Page {url} appears to be a likely article page based on selectors.")
        else:
             # Fallback to URL pattern check if selector check is insufficient
             # Use the COMPILED regex from link_extractor.allow_res
             allow_res_list = self.link_extractor.allow_res or []

             # Check if the URL matches any of the original _allow_patterns that are likely for articles
             article_pattern_strings = [p for p in self._allow_patterns if any(keyword in p for keyword in ['ar-', 'ss-', '/article/', '/story/', '/news/'])]
             article_regexes_for_check = [re.compile(r) for r in article_pattern_strings]

             if any(regex.search(url) for regex in article_regexes_for_check):
                 is_likely_article_page = True # Re-evaluate if it's truly likely an article page
                 self.logger.debug(f"DEBUG: Page {url} appears to be a likely article page based on URL pattern fallback.")
             else:
                  self.logger.debug(f"DEBUG: Page {url} does NOT appear to be a likely article page based on selectors or URL patterns.")


        # Check if it's a core domain and hasn't reached the limit AND is a likely article
        is_core_domain = current_domain in self.core_domains
        domain_count = self.crawled_count_per_domain.get(current_domain, 0)
        should_process_item = is_core_domain and domain_count < self.page_limit_per_domain and is_likely_article_page


        if should_process_item: # Only count and yield if domain limit not reached AND it's a likely article page
            self.crawled_count_per_domain[current_domain] = domain_count + 1
            self.logger.info(f"[{current_domain}] COUNT: {self.crawled_count_per_domain[current_domain]}/{self.page_limit_per_domain}. Yielding ITEM for {url}")

            item = NewsArticleItem()
            item['url'] = url
            item['rendered_html'] = response.text # Store rendered HTML for the pipeline

            # --- Extract basic metadata using Scrapy Selectors ---
            # YOU MUST VERIFY AND UPDATE THESE SELECTORS BY INSPECTING RENDERED ARTICLE PAGES FOR ALL YOUR DOMAINS
            item['title'] = self.safe_css(response, 'h1.main-title::text') or \
                            self.safe_css(response, 'h1[itemprop="headline"]::text') or \
                            self.safe_css(response, 'meta[property="og:title"]::attr(content)') or \
                            self.safe_css(response, 'head title::text') or \
                            self.safe_css(response, 'h1::text')


            item['description'] = self.safe_css(response, 'meta[name="description"]::attr(content)') or \
                                 self.safe_css(response, 'meta[property="og:description"]::attr(content)') or \
                                 self.safe_css(response, 'meta[name="twitter:description"]::attr(content)') or \
                                 self.safe_css(response, '.article-summary::text') or \
                                 self.safe_css(response, 'p[itemprop="description"]::text') or \
                                 self.safe_css(response, '.article-lead-text::text')


            # if not item['description'] and response.css('.article-content p').get(): # Fallback to content
            #      article_paragraphs = response.css('.article-content p::text').getall()
            #      if article_paragraphs:
            #           potential_description = " ".join(article_paragraphs[:3])
            #           item['description'] = potential_description[:300].strip() + "..." if len(potential_description) > 300 else potential_description.strip()


            item['canonical_url'] = self.safe_css(response, 'link[rel="canonical"]::attr(href"]')
            if item['canonical_url']:
                 item['canonical_url'] = urljoin(url, item['canonical_url'])


            # Published Date - Find selector on article pages
            date_str = (
                self.safe_css(response, 'meta[property="article:published_time"]::attr(content)') or
                self.safe_css(response, 'time::attr(datetime)') or
                self.safe_css(response, '.byline .date::text') or
                self.safe_css(response, 'span.publish-date::text') or
                self.safe_css(response, 'div[itemprop="datePublished"]::text') or
                self.safe_css(response, '.article-timestamp::text') or
                 response.xpath('//meta[@property="article:published_time"]/@content').get()
                # *** TO DO: Add actual site-specific date selectors here ***
            )
            item['published_date'] = self.parse_date(date_str)


            # Author - Find selector on article pages
            item['author'] = (
                self.safe_css(response, 'meta[name="author"]::attr(content)') or
                self.safe_css(response, 'meta[property="article:author"]::attr(content)') or
                self.safe_css(response, '.byline .author::text') or
                self.safe_css(response, 'span.author-name::text') or
                self.safe_css(response, 'div[itemprop="author"] [itemprop="name"]::text') or
                self.safe_css(response, '.author-byline a::text')
                # *** TO DO: Add actual site-specific author selectors here ***
            )


            # Categories/Tags - Find selectors on article pages
            item['categories'] = response.css('meta[property="article:section"]::attr(content)').getall() or \
                                 response.css('meta[name="keywords"]::attr(content)').getall() or \
                                 response.css('.breadcrumb a::text').getall()
            item['tags'] = response.css('meta[property="article:tag"]::attr(content)').getall() or \
                           response.css('.article-tags a::text').getall() or \
                           response.css('.tags a::text').getall() or \
                           response.css('.topic a::text').getall()
            item['categories'] = [cat.strip() for cat in item['categories'] if cat and cat.strip()]
            item['tags'] = [tag.strip() for tag in item['tags'] if tag and tag.strip()]
             # Further cleaning might be needed for categories/tags from meta keywords


            yield item

        elif is_core_domain and domain_count >= self.page_limit_per_domain:
             self.logger.info(f"[{current_domain}] Domain limit {self.page_limit_per_domain} reached. Skipping ITEM yield and further link extraction from {url}")
             return
        elif not is_core_domain:
             self.logger.debug(f"[{current_domain}] Not a core domain. Skipping ITEM yield for {url}")
        elif is_core_domain and not is_likely_article_page:
              self.logger.debug(f"[{current_domain}] Not a likely article page. Skipping ITEM yield for {url}")


        # --- Manual Link Extraction and Yielding for Following ---
        if not is_core_domain or domain_count < self.page_limit_per_domain:
             self.logger.debug(f"DEBUG: --- Manually extracting and yielding links from {url} ---")

             # --- Method 1: Use LinkExtractor (finds <a> tags with href) ---
             le = self.link_extractor
             # LinkExtractor automatically applies allow_domains, allow, deny, restrict_css
             # This is still valuable for other sites or basic links on MSN
             links_from_a_href_objs = le.extract_links(response)
             links_from_a_href = [link.url for link in links_from_a_href_objs] # Get just the URLs
             self.logger.debug(f"DEBUG: LinkExtractor (a@href) found {len(links_from_a_href)} links.")


             # --- Method 2: Manually extract destinationurl from specific elements (FOR MSN and similar sites) ---
             manual_extracted_urls = []
             # Search for elements that might have the destinationurl (based on your snippet and inspection)
             # Adjust selectors based on your actual inspection of MSN list pages (RENDERED DOM)
             # Add more selectors here if articles links are within other elements
             # Revisit selectors based on your latest inspection
             msn_link_elements = response.css('cs-responsive-card[destinationurl], social-bar-wc[destinationurl], div[data-m="UniversalFeed"] a, div[data-m="VerticalFeed"] a, a.feed-card-link, a.news-card-link, .feed-item a, .card-title a')
             # Let's try a very broad selector just to see *if* Playwright is getting the content
             # For debugging only: response.css('*[destinationurl], a[href]') # This will find EVERYTHING with href/destinationurl


             self.logger.debug(f"DEBUG: Found {len(msn_link_elements)} potential MSN-style link elements.")

             for element in msn_link_elements:
                 # Try getting 'destinationurl' first, fallback to 'href' if it's an <a> or other tag
                 dest_url = element.attrib.get('destinationurl') or element.attrib.get('href')
                 if dest_url:
                      # Ensure URL is absolute
                      abs_url = urljoin(url, dest_url)
                      manual_extracted_urls.append(abs_url)


             # --- Combine and filter manually extracted URLs ---
             # Combine links from a@href and manual extraction, remove duplicates before filtering
             all_candidate_urls_set = set(links_from_a_href + manual_extracted_urls)
             all_candidate_urls = list(all_candidate_urls_set)
             self.logger.debug(f"DEBUG: Combined unique candidate links: {len(all_candidate_urls)}.")


             filtered_urls = []
             # Use the COMPILED regex from link_extractor.allow_res and deny_res
             allow_res_list = self.link_extractor.allow_res or []
             deny_res_list = self.link_extractor.deny_res or []
             allowed_domains_set = set(self.allowed_domains)


             for candidate_url in all_candidate_urls:
                 try:
                     parsed_url = urlparse(candidate_url)
                     link_domain = parsed_url.netloc.replace("www.", "")

                     # Check against allowed_domains
                     is_allowed_domain = link_domain in allowed_domains_set
                     if not is_allowed_domain:
                          self.logger.debug(f"DEBUG:   Manual Link Filter: {candidate_url} - DENIED (Domain: {link_domain} not in allowed_domains)")
                          continue

                     # Check against allow patterns
                     is_allowed_pattern = any(regex.search(candidate_url) for regex in allow_res_list)
                     if not is_allowed_pattern:
                          self.logger.debug(f"DEBUG:   Manual Link Filter: {candidate_url} - DENIED (Doesn't match allow pattern)")
                          continue

                     # Check against deny patterns
                     is_denied_pattern = any(regex.search(candidate_url) for regex in deny_res_list)
                     if is_denied_pattern:
                          self.logger.debug(f"DEBUG:   Manual Link Filter: {candidate_url} - DENIED (Matches deny pattern)")
                          continue

                     # If passes all filters
                     self.logger.debug(f"DEBUG:   Manual Link Filter: {candidate_url} - ALLOWED")
                     filtered_urls.append(candidate_url)

                 except Exception as e:
                     self.logger.error(f"DEBUG: !!! An ERROR occurred checking manually extracted URL {candidate_url}: {e}")

             # --- REMOVED DupeFilter usage for now ---
             urls_to_yield = filtered_urls # Yield all filtered URLs without deduplication

             self.logger.debug(f"DEBUG: Found {len(urls_to_yield)} NEW valid links to yield after manual extraction and filtering (NO DEDUPLICATION) on {url}.")

             next_request_meta_template = self.PLAYWRIGHT_META_TEMPLATE.copy()

             for i, link_url in enumerate(urls_to_yield):
                 try:
                      parsed_link_url = urlparse(link_url)
                      core_domain_for_next_request = parsed_link_url.netloc.replace("www.", "")

                      next_request_meta = next_request_meta_template.copy()
                      next_request_meta['core_domain_key'] = core_domain_for_next_request

                      self.logger.debug(f"DEBUG: Manually yielding Request {i+1} for: {link_url}")
                      yield scrapy.Request(
                          url=link_url,
                          callback=self.parse_page,
                          meta=next_request_meta,
                          errback=self.on_playwright_error,
                          priority=10,
                          # schedule_replace=True # No effect without DupeFilter
                      )

                 except Exception as e:
                      self.logger.error(f"DEBUG: !!! An ERROR occurred preparing Request for {link_url} manually: {e}")


             self.logger.debug(f"DEBUG: --- Finished manual link yielding from {url} ---")

        else:
             self.logger.debug(f"DEBUG: Skipping link extraction from {url} as domain limit reached for {current_domain}.")


        # Ensure the page is closed if playwright_include_page was True
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