# -*- coding: utf-8 -*-
import scrapy

from lagou.items import PositionItem


class JobSpiderSpider(scrapy.Spider):
    name = 'job_spider'
    allowed_domains = ['lagou.com']
    # start_urls = ['https://www.lagou.com/']

    def start_requests(self):
        url = 'https://www.lagou.com/'
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        for menu_box in response.css('.menu_box'):
            for a in menu_box.css('a'):
                url = a.css('a::attr(href)').extract_first() + '{page}/'
                job = a.css('a::text').extract_first()
                for page in range(1, 31):
                    job_url = url.format(page=str(page))
                    yield scrapy.Request(job_url, callback=self.parse_job_list, meta={'job': job})

    def parse_job_list(self, response):
        job = response.meta.get('job')
        for position in response.css('.item_con_list li'):
            position_url = position.css('.com_logo a::attr(href)').extract_first()
            yield scrapy.Request(position_url, callback=self.parse_detail_job, meta={'job': job})

    def parse_detail_job(self, response):
        item = PositionItem()
        item['job'] = response.meta.get('job')
        item['url'] = response.url
        item['company'] = response.css('img.b2::attr(alt)').extract_first()
        item['position'] = response.css('.job-name::attr(title)').extract_first()
        item['salary'] = response.css('.salary::text').extract_first()
        item['location'] = response.css('.work_addr a::text').extract_first()
        item['advantage'] = response.css('.job-advantage p::text').extract()
        description = response.css('.job_bt p::text').extract()
        index = len(description)
        for i in description:
            if '任职要求' in i:
                index = description.index(i)
                break
        item['duty'] = description[1: index]
        item['requirement'] = description[index + 1:]
        yield item

