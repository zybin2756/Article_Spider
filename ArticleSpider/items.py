# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field()
    vote_nums = scrapy.Field()
    mark_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    crawl_time = scrapy.Field()
    pass