#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import lxml
import random

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http.request import Request

from ..utils import *
from ..items import JpAvItem

# http://www.javlibrary.com/cn/vl_bestrated.php
# http://www.javlibrary.com/cn/vl_newrelease.php
# http://www.javlibrary.com/cn/vl_genre.php?g=da

# http://www.javlibrary.com/cn/?v=javlijrx7a

# http://www.javlibrary.com/cn/star_mostfav.php

# scrapy crawl tb_thread -a target=android -a target=xx -o data/android_threads.json -f json -s LOG_FILE=scrapy_tb_android.log
class JvItemSpider(CrawlSpider):

    name = 'jp_av'
    allowed_domain = ['www.javlibrary.com',]
    magnet_regexp = re.compile('magnet[^<\s]*')
    itemRule = SgmlLinkExtractor(allow=(r'/\?v=jav.*',))
    genreRule = SgmlLinkExtractor(allow=(r'/vl_genre.php\?g=',))
    defaultIdxUrl = 'http://www.javlibrary.com/cn/genres.php'

    def __init__(self, target=None, url=None, action=None, *args, **kwargs):
        # (type: bestrated, genre: name(da), alias(白日出轨))
        super(JvItemSpider, self).__init__(*args, **kwargs)
        if url is None:
            # raise ValueError('Url cant be none for JvItemSpider!')
            self.start_urls = [self.defaultIdxUrl,]
        else:
            self.start_urls = [url,]

    def parse_start_url(self, response):
        if response.url == self.defaultIdxUrl:
            # Todo: random the list
            genreList = self.genreRule.extract_links(response)
            random.shuffle(genreList)
            for i in genreList:
                yield Request(i.url, callback=self.parse_start_url)
        else:
            # self.slug = url.replace('http://www.javlibrary.com', '').replace('.php?','-').replace('.php','')
            # self.alias = parsed.cssselect('.boxtitle')[0].text_content().replace(u'相关的影片','').strip()
            parsed = lxml.html.fromstring(response.body)
            try:
                totalPg = int(parsed.cssselect('.page.last')[0].attrib.get('href').split('page=')[1])
                # Todo: random the list
                pageList = range(totalPg-2)
                random.shuffle(pageList)
                for i in pageList:
                    yield Request(set_query_parameter(response.url, 'page',i+2), callback=self.parse_list, priority=10)
            except Exception as e:
                print e

    def parse_list(self, response):
        for i in self.itemRule.extract_links(response):
            yield Request(i.url, callback=self.parse_thread, priority=100)

    def parse_thread(self, response):
        hxs = HtmlXPathSelector(response)
        items = []
        item = JpAvItem()
        if self.magnet_regexp.findall(response.body):
            item['downloadurl'] = self.magnet_regexp.findall(response.body)[0]
        item['preview'] = hxs.select("//*[@id='video_jacket_img']/@src").extract()[0]
        item['title'] = hxs.select("//h3/a/text()").extract()[0]
        item['slug'] = hxs.select('//*[@id="video_id"]/table/tr/td[2]/text()').extract()[0]
        item['category'] = hxs.select('//*[@class="genre"]/a/text()').extract()
        item['actor'] = hxs.select('//*[@class="star"]/a/text()').extract()
        yield item
