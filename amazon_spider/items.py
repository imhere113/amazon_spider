# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class AmazonSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Name = Field()  # 商品名称
    Asin = Field()  # asin码
    Price_Sale = Field()  # 价格1
    Price_List = Field()  # 价格2
    getTime = Field()  # 最快到货日期
    DateAvailable = Field()  # 最快到货日期
    Stars = Field()  # 星级
    Ratings = Field()  # 评论数量
    BSR_Parent = Field()  # Best Sellers Rank
    BSR_Child = Field()  # Best Sellers Rank
    Weight = Field()  # shipping weight
    Variants = Field()  # 变体类型
    QA = Field()  # 问答数量
    pass
