# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class LagouItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class PositionItem(Item):
    job = Field()           # 工作名称
    url = Field()           # 职位链接
    company = Field()       # 公司名称
    position = Field()      # 职位名称
    salary = Field()        # 薪水
    location = Field()      # 位置
    advantage = Field()     # 职位诱惑
    duty = Field()          # 工作内容
    requirement = Field()   # 岗位职责

