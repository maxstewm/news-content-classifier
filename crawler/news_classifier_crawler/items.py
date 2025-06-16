# news_classifier_crawler/items.py

import scrapy

class NewsArticleItem(scrapy.Item):
    url = scrapy.Field()             # 页面 URL
    # html_content = scrapy.Field()    # 原始 HTML (Playwright 模式下通常为空或不完整)
    rendered_html = scrapy.Field()   # Playwright 渲染后的 HTML (用于提取) - Pipeline 需要这个

    # 直接从 HTML 提取的 metadata (使用 Selector)
    title = scrapy.Field()
    description = scrapy.Field() # 重点优化的字段

    # 扩展提取的元数据字段
    canonical_url = scrapy.Field()   # 规范 URL
    published_date = scrapy.Field()  # 发布日期
    author = scrapy.Field()          # 作者
    categories = scrapy.Field()      # 分类列表
    tags = scrapy.Field()            # 标签列表
    # 可以根据需要添加其他字段，例如：
    # og_title = scrapy.Field()
    # og_description = scrapy.Field()
    # og_image = scrapy.Field()
    # twitter_card = scrapy.Field()
    # twitter_title = scrapy.Field()
    # twitter_description = scrapy.Field()
    # twitter_image = scrapy.Field()


    # 在 Pipeline 中进一步处理后添加的字段
    extracted_core_text = scrapy.Field() # 干净的核心文章内容 (Trafilatura)
    extracted_names = scrapy.Field()     # 提取的名称列表 (SpaCy NER)
    extracted_keywords = scrapy.Field()  # 提取的关键词列表 (SpaCy simple extraction)

    # Placeholder for classification result (added after training)
    # classification_label = scrapy.Field()