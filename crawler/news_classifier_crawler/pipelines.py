import trafilatura
import spacy
import logging
from news_classifier_crawler.items import NewsArticleItem
import gc # Import garbage collector

# Set up logging for the pipeline
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG) # Set level as needed

# Load spaCy English model globally once
# Using a larger model like 'en_core_web_md' or 'en_core_web_lg' might give better results but uses more memory
# 'en_core_web_sm' is the smallest and might be suitable for 4GB RAM
try:
    # Increased timeout for download in case of slow connection
    nlp = spacy.load("en_core_web_sm", disable=["parser", "textcat", "tokenizer"]) # Disable components not needed for NER/POS/token
    logger.info("SpaCy model 'en_core_web_sm' loaded successfully.")
except Exception as e:
    logger.error(f"SpaCy model 'en_core_web_sm' not found or failed to load. Please run 'python -m spacy download en_core_web_sm'. Error: {e}")
    nlp = None

class ContentExtractionPipeline:
    def process_item(self, item, spider):
        # Check if the item is of the type we handle
        if not isinstance(item, NewsArticleItem):
            return item # Pass other item types through

        url = item.get('url', 'N/A')
        spider.logger.debug(f"Pipeline: Processing item for {url}")

        # --- 1. Extract Core Text using Trafilatura ---
        # Use rendered_html from Playwright
        rendered_html = item.get('rendered_html')

        if rendered_html and len(rendered_html) > 100: # Basic check for non-empty HTML
            spider.logger.debug(f"Pipeline: Starting Trafilatura extraction for {url}")
            try:
                # download=False tells Trafilatura to use the provided HTML string
                # Use favor_recall=True to try harder to get content, even if noisy
                # Use include_images=False, include_tables=False etc if only text is needed
                extracted = trafilatura.extract(
                    rendered_html,
                    #download=False,
                    include_comments=False,
                    favor_recall=True,
                    # Additional options to clean output
                    output_format='txt', # Ensure plain text output
                    include_formatting=False,
                    include_links=False,
                    # silence=True # Suppress Trafilatura internal warnings (optional)
                )
                item['extracted_core_text'] = extracted.strip() if extracted else ""

                if not item['extracted_core_text']:
                    spider.logger.warning(f"Pipeline: Trafilatura extraction EMPTY for {url}")
                else:
                     spider.logger.debug(f"Pipeline: Trafilatura extracted {len(item['extracted_core_text'])} characters from {url}")


            except Exception as e:
                spider.logger.error(f"Pipeline: Trafilatura extraction failed for {url}: {e}")
                item['extracted_core_text'] = ""
        else:
             spider.logger.warning(f"Pipeline: No rendered_html or HTML too short for Trafilatura processing: {url}")
             item['extracted_core_text'] = "" # Ensure field exists even if empty


        # --- 2. Perform NLP tasks (Named Entities, Keywords) if core text was extracted ---
        core_text = item.get('extracted_core_text')
        if core_text and nlp:
            # Limit processing to avoid excessive memory/CPU if core text is huge, or just process everything
            # if len(core_text) > 100000: # Example: skip NLP for very long texts
            #      spider.logger.warning(f"Pipeline: Skipping NLP for very long text ({len(core_text)} chars) from {url}")
            #      item['extracted_names'] = []
            #      item['extracted_keywords'] = []
            #      # Manually trigger garbage collection after potentially large text processing
            #      gc.collect()
            # else:
                try:
                    spider.logger.debug(f"Pipeline: Starting SpaCy processing for {url}")
                    # Process the text with spaCy
                    # nlp processes in batches for efficiency, especially with larger texts
                    doc = nlp(core_text)

                    # Extract Names (PER, ORG, GPE)
                    names = [ent.text for ent in doc.ents if ent.label_ in ["PER", "ORG", "GPE"]]
                    item['extracted_names'] = list(set(names)) # Get unique names

                    # Extract Keywords (Example: frequent non-stopword nouns)
                    # This is a simple approach. More advanced keyword extraction would consider
                    # TF-IDF or TextRank over the whole corpus.
                    # Using Counter requires importing it: from collections import Counter
                    from collections import Counter
                    keywords = [token.text.lower() for token in doc if token.pos_ == "NOUN" and not token.is_stop and token.text.isalpha()] # Only alphabetic nouns
                    keyword_counts = Counter(keywords)
                    # Get top 10 most common keywords (nouns)
                    item['extracted_keywords'] = [kw for kw, count in keyword_counts.most_common(10)]

                    spider.logger.debug(f"Pipeline: SpaCy extracted {len(item['extracted_names'])} names and {len(item['extracted_keywords'])} keywords from {url}")


                except Exception as e:
                    spider.logger.error(f"Pipeline: SpaCy processing failed for {url}: {e}")
                    item['extracted_names'] = []
                    item['extracted_keywords'] = []
                finally:
                    # Manually trigger garbage collection to free up memory used by spaCy docs
                    # SpaCy objects can be large and GC might not run immediately
                    del doc # Explicitly delete the doc object
                    gc.collect()
                    spider.logger.debug(f"Pipeline: SpaCy processing finished, GC called for {url}")

        else:
             # No core text extracted or NLP model not loaded
             spider.logger.debug(f"Pipeline: Skipping NLP processing (no core text or nlp model) for {url}")
             item['extracted_names'] = []
             item['extracted_keywords'] = []


        # Remove rendered_html to save memory once processing is done in the pipeline
        # unless you need it later. For evaluation data, keeping it might be useful.
        # Consider commenting this out if you need rendered_html for subsequent steps.
        # if 'rendered_html' in item:
        #      del item['rendered_html']
        #      spider.logger.debug(f"Pipeline: Removed rendered_html from item for {url}")


        spider.logger.debug(f"Pipeline: Finished processing item for {url}")
        return item

    # Optional: implement spider_opened/closed if you need to manage resources per spider instance
    # def spider_opened(self, spider):
    #     logger.info(f"Pipeline spider opened: {spider.name}")

    # def spider_closed(self, spider):
    #     logger.info(f"Pipeline spider closed: {spider.name}")