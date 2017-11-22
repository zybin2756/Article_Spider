# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from urllib import parse
from ArticleSpider.items import JobboleArticleItem
from ArticleSpider.utils.commom import get_md5
from ArticleSpider.items import mArticleItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/page/294']

    def parse(self, response):
        items = response.css(".post-thumb")
        for item in items:
            url = item.css("a::attr(href)").extract_first()
            img_url = item.css("img::attr(src)").extract_first()
            yield scrapy.Request(url=parse.urljoin(response.url, url),meta={"img_url":parse.urljoin(response.url, img_url)},callback=self.parse_article)

        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield scrapy.Request(url=parse.urljoin(response.url, next_url),callback=self.parse)

    def parse_article(self, response):
        # 解析文章
        img_url = response.meta.get("img_url", "")
        itemLoader = mArticleItemLoader(item=JobboleArticleItem(),response=response)
        itemLoader.add_css("title",".entry-header h1::text")
        itemLoader.add_css("create_time", ".entry-meta-hide-on-mobile::text")
        itemLoader.add_css("mark_nums", ".bookmark-btn::text")
        itemLoader.add_css("comment_nums", ".btn-bluet-bigger.href-style.hide-on-480::text")
        itemLoader.add_css("vote_nums", ".vote-post-up h10::text")
        itemLoader.add_css("content", ".entry")
        itemLoader.add_value("crawl_time",datetime.now().strftime("%Y/%m/%d"))
        itemLoader.add_value("url",response.url)
        itemLoader.add_value("img_url",[img_url])
        itemLoader.add_value("object_id",get_md5(response.url))
        item = itemLoader.load_item()
        yield item