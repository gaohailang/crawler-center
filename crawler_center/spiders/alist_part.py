#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
from ..items import AListApartItem

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

class CSSItemSpider(CrawlSpider):

    name = 'a_list_apart'
    allowed_domain = ['alistapart.com']
    rules = (Rule(SgmlLinkExtractor(allow=(r'/articles/archives/.*',)), callback='parse_thread', follow=True),)
    start_urls = ['http://alistapart.com/articles/archives/0']

    def parse_thread(self, response):
        hxs = HtmlXPathSelector(response)
        threads = hxs.select("//*[@class='entry-list']/li")

        for t in threads:
            item = AListApartItem()
            try:
                item['postnum'] = int(t.select('.//*[@class="comment-count"]/text()').extract()[0].replace('Comments','').strip())
            except:
                item['postnum'] = 0
            item['title'] = t.select('.//h3/a/text()').extract()[0]
            item['url'] = t.select('.//h3/a/@href').extract()[0]
            item['date'] = t.select('.//*[@class="pubdate updated"]/text()').extract()[0]
            yield item
