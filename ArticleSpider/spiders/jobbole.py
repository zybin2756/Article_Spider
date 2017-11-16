# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from ArticleSpider.items import JobboleArticleItem

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        items = response.css(".post-thumb")
        for item in items:
            url = item.css("a::attr(href)").extract_first()
            img_url = item.css("img::attr(src)").extract_first()
            yield scrapy.Request(url=url,meta={"img_url":img_url},callback=self.parse_article)

        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield scrapy.Request(url=next_url,callback=self.parse)

    def parse_article(self, response):
        # 解析文章
        itemLoader = ItemLoader(item=JobboleArticleItem(),response=response)
        
        pass