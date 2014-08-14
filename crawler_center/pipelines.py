# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
# from .items import JpAvItemId

from pymongo import Connection
MongoCon = Connection('localhost', 27017) # the default is 27017
MiscDB = MongoCon.misc

import urllib

SPEC_DB = ['tb_user', 'tb_thread', 'tb_fidfname', 'wb_userstatus', 'jp_av']


class MongoPipeline(object):

    def __init__(self):
        self.seenDict = dict()
        self.seenDict['jp_av'] = [i['slug'] for i in MongoCon.jp_av.items.find()]

    def process_item(self, item, spider):
        if hasattr(spider, 'alias'):
            alias = urllib.unquote(spider.alias)
        if spider.name == 'jp_av':
            if item['slug'] in self.seenDict['jp_av']:
                raise DropItem('Duplicate item found: %s' % item)
            # alias = urllib.unquote(spider.slug)
            MongoCon.jp_av.items.insert(dict(item))
            self.seenDict['jp_av'].append(item['slug'])
            return item
        if spider.name in SPEC_DB:
            # getattr(MongoCon, spider.name).insert(dict(item))
            MongoCon[spider.name][alias].insert(dict(item))
        else:
            MiscDB[spider.name].insert(dict(item))
        return item
