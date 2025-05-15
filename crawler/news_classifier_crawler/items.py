# items.py
import scrapy

class NewsArticleItem(scrapy.Item):
    url = scrapy.Field()             # 页面 URL
    html_content = scrapy.Field()    # 抓取到的原始 HTML (可选，但方便调试和后续处理)
    rendered_html = scrapy.Field()   # Playwright 渲染后的 HTML (用于提取)

    # 直接从 HTML 提取的 metadata
    title = scrapy.Field()
    description = scrapy.Field() # 重点优化的字段

    # 在 Pipeline 中进一步处理后添加的字段
    extracted_core_text = scrapy.Field() # 干净的核心文章内容
    extracted_names = scrapy.Field()     # 提取的名称列表 (NER)
    extracted_keywords = scrapy.Field()  # 提取的关键词列表

    # Placeholder for classification result (added after training)
    # classification_label = scrapy.Field()