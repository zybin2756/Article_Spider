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


class mArticleItemLoader(ItemLoader):
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

#  CREATE TABLE IF NOT EXISTS `zhihu_question` (
#   `title` varchar(100) COLLATE utf8_bin NOT NULL,
#   `detail` text COLLATE utf8_bin NOT NULL,
#   `comment_nums` int(11) NOT NULL,
#   `attention_nums` int(11) NOT NULL,
#   `watch_nums` int(11) NOT NULL,
#   `tags` varchar(100) COLLATE utf8_bin NOT NULL,
#   `crawl_time` date NOT NULL,
#   `url` varchar(300) COLLATE utf8_bin NOT NULL,
#   `object_id` char(32) COLLATE utf8_bin NOT NULL,
#   `question_id` int(11) COLLATE utf8_bin NOT NULL,
#   PRIMARY KEY (`object_id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
#https://www.zhihu.com/api/v4/questions/21458823/answers?limit=20&offset=0&include=data[*].is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees&data[*].author.follower_count%2Cbadge[%3F(type=best_answerer)].topics&data[*].mark_infos[*].url=&sort_by=default


class ZhihuQuestionItem(scrapy.Item):
    title = scrapy.Field()
    detail = scrapy.Field()
    comment_nums = scrapy.Field(input_processor=MapCompose(strip,get_nums))
    attention_nums = scrapy.Field()
    watch_nums = scrapy.Field()
    tags = scrapy.Field(output_processor=MapCompose(return_value))
    crawl_time = scrapy.Field()
    url = scrapy.Field()
    object_id = scrapy.Field()
    question_id = scrapy.Field()

    def get_insert_sql(self):
        sql = "INSERT INTO `zhihu_question`(`title`, `detail`, `comment_nums`, `attention_nums`, " \
              "`watch_nums`, `tags`, `crawl_time`, `url`, `object_id`,`question_id`) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE comment_nums=VALUES(comment_nums)" \
              ",attention_nums=VALUES(attention_nums),watch_nums=VALUES(watch_nums),crawl_time=VALUES(crawl_time)"

        self["tags"] = ",".join(self["tags"])

        params = (self["title"], self["detail"], self["comment_nums"], self["attention_nums"],
                  self["watch_nums"], self["tags"], self["crawl_time"], self["url"],
                  self["object_id"],self["question_id"])

        return sql, params


# CREATE TABLE `zhihu_answer` (
#   `object_id` char(32) COLLATE utf8_bin NOT NULL,
#   `answer_id` int(11) NOT NULL,
#   `question_id` int(11) NOT NULL,
#   `author_id` varchar(32) COLLATE utf8_bin NOT NULL,
#   `created_time` date NOT NULL,
#   `voteup_count` int(11) NOT NULL,
#   `url` varchar(300) COLLATE utf8_bin NOT NULL,
#   `updated_time` date NOT NULL,
#   `crawl_time` date NOT NULL,
#   `content` text COLLATE utf8_bin NOT NULL,
#   `comment_count` int(11) NOT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
class ZhihuAnswerItem(scrapy.Item):
    object_id = scrapy.Field()
    answer_id = scrapy.Field()
    question_id = scrapy.Field()
    created_time = scrapy.Field()
    voteup_count = scrapy.Field()
    url = scrapy.Field()
    updated_time = scrapy.Field()
    crawl_time = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    comment_count = scrapy.Field()

    def get_insert_sql(self):
        sql = "INSERT INTO `zhihu_answer`(`object_id`, `answer_id`, `question_id`, `author_id`, " \
              "`created_time`, `voteup_count`, `url`, `updated_time`, `crawl_time`, `content`, `comment_count`) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE comment_count=VALUES(comment_count)" \
              ",voteup_count=VALUES(voteup_count),content=VALUES(content),crawl_time=VALUES(crawl_time)"

        params = (self["object_id"], self["answer_id"], self["question_id"], self["author_id"],
                  self["created_time"], self["voteup_count"], self["url"], self["updated_time"],
                  self["crawl_time"],self["content"],self["comment_count"])

        return sql, params


class LaGouJobItem(scrapy.Item):
    job_name = scrapy.Field()
    job_company = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    position_type = scrapy.Field()
    job_request = scrapy.Field()
    publish_time = scrapy.Field()
    crawl_time = scrapy.Field()
    work_addr = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    object_id = scrapy.Field()


