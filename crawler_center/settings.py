# Scrapy settings for crawler_center project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'crawler_center'

SPIDER_MODULES = ['crawler_center.spiders']
NEWSPIDER_MODULE = 'crawler_center.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler_center (+http://www.yourdomain.com)'

ITEM_PIPELINES = [
    'crawler_center.pipelines.FilterDupPipeline',
    'crawler_center.pipelines.MongoPipeline',
]
