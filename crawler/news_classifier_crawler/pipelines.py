# pipelines.py
import trafilatura
import spacy
import logging
from news_classifier_crawler.items import NewsArticleItem

# Load spaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    logging.error("SpaCy model not found. Please run 'python -m spacy download en_core_web_sm'")
    nlp = None


class ContentExtractionPipeline:
    def process_item(self, item, spider):
        spider.logger.info(f"DEBUG: Entering ContentExtractionPipeline for {item.get('url')}") # 添加这行
        if isinstance(item, NewsArticleItem):
            # --- 1. Extract Core Text using Trafilatura ---
            # Use rendered_html from Playwright if available, fallback to html_content
            html_content = item.get('rendered_html') or item.get('html_content')

            if html_content:
                spider.logger.debug(f"DEBUG: Pipeline: Starting Trafilatura extraction for {item.get('url')}") # 添加打印
                try:
                    # download=False means trafilatura works on the provided HTML string
                    # Include comments=False, favor_recall=True etc based on needs
                    extracted = trafilatura.extract(html_content, include_comments=False, favor_recall=True)
                    if extracted:
                        item['extracted_core_text'] = extracted.strip()
                    else:
                         item['extracted_core_text'] = "" # Or handle as extraction failure

                    item['extracted_core_text'] = extracted.strip() if extracted else ""
                    if not item['extracted_core_text']:
                        spider.logger.warning(f"DEBUG: Core text extraction EMPTY for {item.get('url')}") # 核心文本提取失败

                except Exception as e:
                    spider.logger.error(f"Trafilatura extraction failed for {item.get('url')}: {e}")
                    item['extracted_core_text'] = ""

            # --- 2. Extract Names (Named Entities) using spaCy ---
            core_text = item.get('extracted_core_text')
            if core_text and nlp:
                #spider.logger.warning(f"DEBUG: Core text extraction EMPTY for {item.get('url')}. Item will still pass.") # 添加这行
                try:
                    doc = nlp(core_text)
                    # Extract PER (Person), ORG (Organization), GPE (Geo-Political Entity) entities
                    names = [ent.text for ent in doc.ents if ent.label_ in ["PER", "ORG", "GPE"]]
                    item['extracted_names'] = list(set(names)) # Use set to get unique names
                    if not item['extracted_names']:
                        spider.logger.debug(f"DEBUG: Names extraction EMPTY for {item.get('url')}")

                except Exception as e:
                    spider.logger.error(f"SpaCy NER failed for {item.get('url')}: {e}")
                    item['extracted_names'] = []
            else:
                 item['extracted_names'] = []
                 if core_text:
                    spider.logger.debug(f"DEBUG: Keywords extraction skipped (no NLP model or core text) for {item.get('url')}")


            # --- 3. Extract Keywords (Simple Example: TF-IDF or TextRank require more context/libraries) ---
            # For a simple demo, let's just use spaCy noun chunks or common nouns as potential keywords
            # A more robust keyword extraction would use TF-IDF across the whole corpus
            if core_text and nlp:
                 try:
                     doc = nlp(core_text)
                     # Example: Extract most frequent non-stopword nouns
                     keywords = [token.text.lower() for token in doc if token.pos_ == "NOUN" and not token.is_stop]
                     # Count frequency and take top N
                     from collections import Counter
                     keyword_counts = Counter(keywords)
                     item['extracted_keywords'] = [kw for kw, count in keyword_counts.most_common(10)] # Top 10 nouns
                     if not item['extracted_keywords']:
                        spider.logger.debug(f"DEBUG: Keywords extraction EMPTY for {item.get('url')}")
                     else:
                        item['extracted_keywords'] = []
                        if core_text:
                            spider.logger.debug(f"DEBUG: Keywords extraction skipped (no NLP model or core text) for {item.get('url')}")


                 except Exception as e:
                      spider.logger.error(f"Keyword extraction failed for {item.get('url')}: {e}")
                      item['extracted_keywords'] = []
            else:
                 spider.logger.warning(f"DEBUG: No rendered_html in item for Pipeline processing: {item.get('url')}") # 没有渲染后的 HTML
                 item['extracted_core_text'] = ""
                 item['extracted_names'] = []
                 item['extracted_keywords'] = []

        spider.logger.info(f"DEBUG: >>> Exiting ContentExtractionPipeline for {item.get('url')}. Extracted core text length: {len(item.get('extracted_core_text', ''))}, Names count: {len(item.get('extracted_names', []))}, Keywords count: {len(item.get('extracted_keywords', []))}") # 确认 Pipeline 处理结果
        
        return item

    # You might add spider_opened and spider_closed methods here if needed
    # e.g., to initialize/clean up resources