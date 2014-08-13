# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field

def ItemClassFactory(name, keys):
    return type(name, (Item, ), dict((key, Field()) for key in keys))

# Tieba Related
TbUser = ItemClassFactory('TbUser', ['name'])
TbFidFname = ItemClassFactory('TbFidFname', ['fname', 'fid'])
TbThread = ItemClassFactory('TbThread', ['title', 'url', 'postnum'])

# Weibo
WbUserstatus = ItemClassFactory('WbUserstatus', 'sid, text, url, retweetnum, commentnum, pdate, favonum'.split(', '))

# css-trick & alistpart article
AListApartItem = ItemClassFactory('AListApartItem', ['title', 'url', 'postnum', 'date'])
CssTricksArticlesItem = ItemClassFactory('CssTricksArticlesItem', ['title', 'url', 'postnum', 'date'])

# jp av
JvItem = ItemClassFactory('JvItem', 'title,slug,category,preview,downloadurl,actor')