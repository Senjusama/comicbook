# coding: UTF-8
import requests
import re
import logging
from requests.exceptions import ConnectionError
import ua
from lxml import etree
import config

from config import DOMAIN



logger = logging.getLogger("spider")
logger.setLevel(logging.INFO)

class NhentaiSpider:
    def __init__(self, url):
        self.url = url

    def crawl(self, item, thread):
        match = re.search(r'nhentai.net/g/\d+', self.url)
        if not match:
            logger.info(" url not match")
            return None
        if 'https' not in self.url:
            self.url = 'https://' + self.url

        session = requests.Session()
        session.headers.update({'User-Agent': ua.getRandomUA()})
        session.proxies.update(config.PROXY)

        try:
            logger.info("fetching "+self.url)
            r = session.get(self.url)
            item.cookies = r.cookies

            selector = etree.HTML(r.text)

            jp_title = selector.xpath('//*[@id="info"]/h2/text()')[0]
            en_title = selector.xpath('//*[@id="info"]/h1/text()')[0]
            item.titles = [jp_title, en_title]
            item.author = selector.xpath('//*[@id="tags"]/div[4]/span/a/text()')

            item.tags = selector.xpath('//*[@id="tags"]/div[3]/span/a/text()')
            item.image_urls = selector.xpath('//*[@id="thumbnail-container"]/div/a/img/@data-src')
            item.image_urls = list(map(convert_url, item.image_urls))
            item.source = self.url
            thread.progress = 0.05
            return item
        except ConnectionError as e:
            print(e)
            return None


def convert_url(url):
    match_type = re.search(r'jpg|png$', url)
    type = match_type.group()
    match_url = re.search(r'\.nhentai\.net/galleries/(\d+)/(\d+)', url)
    id = match_url.group(1)
    index = match_url.group(2)
    return "https://i.nhentai.net/galleries/%s/%s.%s" % (id, index, type)