# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from w3lib.html import  remove_tags


class ArticleLoaderItem(ItemLoader):
    default_output_processor = TakeFirst()


def strip(str):
    return str.strip()


def deal_time(str):
    return str.strip().replace("·","").strip()


def get_nums(str):
    match_obj = re.match(r".*?(\d+).*",str)
    if match_obj:
        return match_obj.group(1)
    return 0


def return_value(value):
    return value


#  create sql
#  CREATE TABLE `article_spider`.`jobbole_article` ( `object_id` CHAR(32) NOT NULL , `title` VARCHAR(100) NOT NULL , `create_time` DATETIME NOT NULL , `crawl_time` DATETIME NOT NULL , `vote_nums` INT NOT NULL , `mark_nums` INT NOT NULL , `comment_nums` INT NOT NULL , `url` VARCHAR(200) NOT NULL , `img_path` VARCHAR(200) NOT NULL , `content` TEXT NOT NULL , PRIMARY KEY (`object_id`)) ENGINE = MyISAM;
class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field(input_processor=MapCompose(deal_time))
    vote_nums = scrapy.Field(input_processor=MapCompose(strip,get_nums))
    mark_nums = scrapy.Field(input_processor=MapCompose(strip,get_nums))
    comment_nums = scrapy.Field(input_processor=MapCompose(strip,get_nums))
    crawl_time = scrapy.Field()
    url = scrapy.Field()
    object_id = scrapy.Field()
    img_path = scrapy.Field()
    content = scrapy.Field()
    img_url = scrapy.Field(output_processor=MapCompose(return_value))

    def get_insert_sql(self):
        sql = "INSERT INTO `jobbole_article`(`object_id`, `title`, `create_time`, " \
                "`crawl_time`, `vote_nums`, `mark_nums`, `comment_nums`, `url`, `img_path`, `content`)" \
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE vote_nums=VALUES(vote_nums)," \
                "mark_nums=VALUES(mark_nums),comment_nums=VALUES(comment_nums),crawl_time=VALUES(crawl_time)"

        # img_path = self['img_path'][0]['path']

        params = (self["object_id"], self["title"], self["create_time"], self["crawl_time"],
                  self["vote_nums"], self["mark_nums"], self["comment_nums"],self["url"],
                  self["img_url"], self["content"])

        return sql,params