# -*- coding: utf-8 -*-
import scrapy
import json
import time
import re
from urllib import parse
from ArticleSpider.items import QuestionItemLoader,AnswerItemLoader,ZhihuQuestionItem,ZhihuAnswerItem
from ArticleSpider.utils.commom import get_md5
from datetime import datetime

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login"
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?limit=20&offset=0&include=data[*]." \
                       "is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2" \
                       "Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count" \
                       "%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_" \
                       "permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship." \
                       "is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees&data[*]." \
                       "author.follower_count%2Cbadge[%3F(type=best_answerer)].topics&data[*].mark_infos[*]" \
                       ".url=&sort_by=default"
    headers = {
        "Host":"www.zhihu.com",
        "Referer":"https://www.zhihu.com/",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    def start_requests(self):
        return [scrapy.Request(url="https://www.zhihu.com/", headers=self.headers, callback=self.check_login)]        #

    def get_captcha(self,response):

        match_obj = re.findall(r'.*?name="_xsrf" value="(.*?)"', response.text)
        xsrf = match_obj[0]

        t = int(time.time()*1000)
        captcha_url = self.captcha_url.format(t)
        return [scrapy.Request(url=captcha_url, headers=self.headers, meta={"xsrf":xsrf},callback=self.login)]

    def login(self,response):
        with open('cap.jpg', 'wb') as fp:
            fp.write(response.body)

        captcha_code = input("> pls input code:")
        data ={
            "_xsrf": response.meta['xsrf'],
            "phone_num": "13726848420",
            "password": "zybzhihu1",
            "captcha":captcha_code
        }
        post_url = "https://www.zhihu.com/login/phone_num"
        return [scrapy.FormRequest(url=post_url, headers=self.headers, formdata=data, callback=self.login_result)]

    def login_result(self,response):
        msg = json.loads(response.body)
        print(msg)
        if msg["r"] == 0:
            for url in self.start_urls:
                yield scrapy.Request(url=url, headers=self.headers,dont_filter=True,callback=self.parse)

    def check_login(self,response):
        match_obj = re.findall(r'.*?/settings/profile.*?',response.text)
        if len(match_obj) > 0:
            for url in self.start_urls:
                yield scrapy.Request(url=url, headers=self.headers,dont_filter=True,callback=self.parse)
        else:
            yield scrapy.Request(url="https://www.zhihu.com/#signin", dont_filter=True, headers=self.headers, callback=self.get_captcha)

    def parse(self, response):
        links = response.css("a::attr(href)").extract()
        # links = [link for link in links if re.match(r".*?question/.*?",link)]
        links = [parse.urljoin(response.url, link) for link in links]

        for url in links:
            match_obj = re.match(r'(.*?question/(\d+)).*?', url)
            if match_obj:
                url = match_obj.group(1)

                yield scrapy.Request(url=url, headers=self.headers,meta={"id":match_obj.group(2)},callback=self.parse_question)
            else:
                yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        itemloader = QuestionItemLoader(item=ZhihuQuestionItem(), response=response)
        itemloader.add_css("title", ".QuestionHeader-title::text")
        itemloader.add_css("detail", ".QuestionHeader-detail")
        itemloader.add_css("comment_nums", ".QuestionHeader-Comment button::text")
        itemloader.add_css("attention_nums", ".Button.NumberBoard-item .NumberBoard-value::text")
        itemloader.add_css("watch_nums", "div.NumberBoard-item > div:nth-child(2)::text")
        itemloader.add_css("tags", ".Popover div::text")
        itemloader.add_value("crawl_time", datetime.now().strftime("%Y/%m/%d"))
        itemloader.add_value("url", response.url)
        itemloader.add_value("object_id", get_md5(response.url))
        itemloader.add_value("question_id", response.meta.get("id"))
        item = itemloader.load_item()

        answer_url = self.start_answer_url.format(response.meta.get("id"))
        yield scrapy.Request(url=answer_url, headers=self.headers,callback=self.parse_answer)
        yield item

    def parse_answer(self, response):
        data = json.loads(response.text)

        for answer in data['data']:
            itemloader = AnswerItemLoader(item=ZhihuAnswerItem(), response=response)
            itemloader.add_value('object_id',get_md5(answer['url']))
            itemloader.add_value('answer_id', answer['id'])
            itemloader.add_value('question_id', answer['question']['id'])
            itemloader.add_value('voteup_count', answer['voteup_count'])
            itemloader.add_value('author_id', answer['author']['id'])
            itemloader.add_value('content', answer['content'])
            itemloader.add_value('comment_count', answer['comment_count'])
            itemloader.add_value('url', answer['url'])
            itemloader.add_value('updated_time', datetime.fromtimestamp(answer['updated_time']).strftime("%Y/%m/%d"))
            itemloader.add_value('crawl_time', datetime.now().strftime("%Y/%m/%d"))
            itemloader.add_value('created_time', datetime.fromtimestamp(answer['updated_time']).strftime("%Y/%m/%d"))

            item = itemloader.load_item()
            yield item
        if not data['paging']['is_end']:
            next_url = data['paging']['next']
            yield scrapy.Request(url=next_url, headers=self.headers, callback=self.parse_answer)