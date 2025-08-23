import scrapy

class GoogleNewsItem(scrapy.Item):
    title = scrapy.Field()
    summary = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    published_time = scrapy.Field()
    keyword = scrapy.Field()
    content_hash = scrapy.Field() 