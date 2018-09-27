# -*- coding: utf-8 -*-
"""
@Time   : 2018/9/15 15:12
@File   : main.py
@Author : ZZShi
程序作用：

"""
from scrapy import cmdline


cmdline.execute('scrapy crawl job_spider'.split())
