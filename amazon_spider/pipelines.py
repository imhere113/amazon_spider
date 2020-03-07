# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

class AmazonSpiderPipeline(object):
    def __init__(self):
        self.filename = open("item.json", "wb")
    def process_item(self, item, spider):
        jsontext=json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.filename.write(jsontext.encode("utf-8"))
        return item
    def close_spider(self,spider):
           self.filename.close()