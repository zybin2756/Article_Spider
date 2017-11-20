# -*- coding: utf-8 -*-
import scrapy
import json
import time
import re

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login"

    headers = {
        "Host":"www.zhihu.com",
        "Referer":"https://www.zhihu.com/",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    def start_requests(self):
        return [scrapy.Request(url="https://www.zhihu.com/#signin", headers=self.headers, callback=self.get_captcha)]

    def get_captcha(self,response):

        match_obj = re.findall(r'.*?name="_xsrf" value="(.*?)"', response.text)
        xsrf = match_obj[0]

        t = int(time.time()*1000)
        captcha_url = self.captcha_url.format(t)
        return [scrapy.Request(url=captcha_url, headers=self.headers,meta={"xsrf":xsrf},callback=self.login)]

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
        return [scrapy.FormRequest(url=post_url,formdata=data,callback=self.login_result)]

    def login_result(self,response):
        msg = json.loads(response.body)
        print(msg)
        if msg["r"] == 0:
            for url in self.start_urls:
                yield scrapy.Request(url=url,dont_filter=True,callback=self.parse)
        pass

    def parse(self, response):
        print(response.body)
        pass
