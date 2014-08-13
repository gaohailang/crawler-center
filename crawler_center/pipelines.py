# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem

from pymongo import Connection
MongoCon = Connection('localhost', 27017) # the default is 27017
MiscDB = MongoCon.misc

SPEC_DB = ['tb_user', 'tb_thread', 'tb_fidfname', 'wb_userstatus', 'jp_av']

class FilterDupPipeline(object):
    def __init__(self):
        self.seenDict = dict()
        # or read from conf db?!

    def process_item(self, item, spider):
        # get unique key from spider config to filter
        if item.get('xx','') in self.seenDict:
            raise DropItem('Duplicate item found: %s' % item)
        return item

class MongoPipeline(object):

    def process_item(self, item, spider):
        if spider.name in SPEC_DB:
            getattr(MongoCon, spider.name).insert(dict(item))
        else:
            MiscDB[spider.name].insert(dict(item))
        return item