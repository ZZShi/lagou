# -*- coding: utf-8 -*-
"""
@Time   : 2018/9/16 16:39
@File   : lagou.py
@Author : ZZShi
程序作用：
    拉勾网全站爬虫，可以爬取拉勾主页所有细分职位
"""
import json
import time
from random import uniform

import requests
import pymongo
from lxml import etree


def get_random_proxy():
    """
    对接代理池，获得随机代理
    :return:
    """
    url = 'http://127.0.0.1:5000/random'
    try:
        r = requests.get(url)
        r.raise_for_status()
        print('正在使用代理：', r.text)
        proxy = {
            'http': 'http://' + r.text,
            'https': 'https://' + r.text
        }
        return proxy
    except ConnectionError:
        print('代理获取失败！！！')
        return None


def get_random_cookies():
    """
    对接cookies池，获得随机cookies
    :return:
    """
    url = 'http://127.0.0.2:5000/lagou/random'
    try:
        r = requests.get(url)
        r.raise_for_status()
        # print('正在使用cookies：', r.text)
        cookies = json.loads(r.text)
        return cookies
    except ConnectionError:
        print('cookies获取失败！！！')
        return None


def get_doc(url):
    """
    获得网页的通用方法
    :param url: url
    :return: 返回一个可以直接使用xpath解析的对象
    """
    hd = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/70.0.3534.4 Safari/537.36'
    }
    try:
        # proxy = get_random_proxy()
        cookies = get_random_cookies()
        r = requests.get(url, headers=hd, cookies=cookies)
        r.raise_for_status()
        doc = etree.HTML(r.text)
        return doc
    except Exception as e:
        print('失败链接：', url)
        print('失败原因：', e.args)
        return None


def parse_job_dict(doc):
    """
    从主页中解析出工作名称和工作的链接
    :param doc:
    :return:
    """
    item = {}
    for a in doc.xpath('//div[@class="menu_box"]/div[@class="menu_sub dn"]//a'):
        job = a.xpath('./text()')[0]
        # MangoDb中存储的键名中不能带'.'
        if '.' in job:
            job = job.replace('.', '*')
        url = a.xpath('./@href')[0]
        item[job] = url
    return item


def parse_position_list(doc):
    """
    从职位列表中解析出职位的url
    :param doc:
    :return:
    """
    for li in doc.xpath('//ul[@class="item_con_list"]/li'):
        url = li.xpath('.//div[@class="p_top"]/a/@href')[0]
        yield url


def parse_position_detail(doc):
    """
    从职位的详细页面中解析出感兴趣的信息
    :param doc:
    :return:
    """
    # 工作职责与职位要求写在一起，需要将其分离出来
    description = doc.xpath('//dd[@class="job_bt"]/div//text()')
    description = list(filter(lambda x: '\n' not in x, description))
    index = len(description)
    for i in description:
        if '要求' in i or '任职' in i or '职位' in i:
            index = description.index(i)
            break
    info = {
        'company': doc.xpath('//img[@class="b2"]/@alt')[0].strip(),
        'salary': doc.xpath('//span[@class="salary"]/text()')[0],
        'position': doc.xpath('//div[@class="job-name"]/@title')[0],
        'location': doc.xpath('//dd[@class="job_request"]/p/span/text()')[1].split('/')[1].strip(),
        'advantage': doc.xpath('//dd[@class="job-advantage"]/p/text()')[0],
        'duty': description[1: index],
        'requirement': description[index + 1:]
    }
    return info


def retry(position_url):
    """
    失败重试函数
    :param position_url:
    :return:
    """
    try:
        doc = get_doc(position_url)
        info = parse_position_detail(doc)
        return info
    except:
        print('Retrying...')
        info = retry(position_url)
        return info


def main():
    start = time.time()
    url = 'https://www.lagou.com'
    my_client = pymongo.MongoClient()
    my_db = my_client['lagou']

    job_html = get_doc(url)
    for job, job_url in parse_job_dict(job_html).items():
        my_col = my_db[job]
        for page in range(1, 31):
            url_job = job_url + '{page}/?filterOption={page}'.format(page=page)
            position = get_doc(url_job)
            for position_url in parse_position_list(position):
                info = retry(position_url)
                info['job'] = job
                info['url'] = position_url
                print(info)
                my_col.update({'url': info['url']}, {'$set': info}, upsert=True)
                time.sleep(uniform(1, 5))
    end = time.time()
    print('Time:{}s'.format(end - start))


if __name__ == '__main__':
    main()
