

import scrapy
from numpy import unicode
import numpy

from ..items import SteamcoderItem
import re


class SteamProductSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    allowed_domains = ['steampowered.com']
    start_urls = ['https://store.steampowered.com/search/?term=minecraft',
                  'https://store.steampowered.com/search/?term=races',
                  'https://store.steampowered.com/search/?term=cosmos']
    urls_of_pages = []
    cur_page = start_urls[0]

    def parse(self, response):

        pages = response.xpath('//*[@class="search_pagination_right"]/a/@href').extract()
        page = pages[0]
        page = page[:-1]
        i = 1

        while i <= 2:
            page = page + str(i)
            i += 1
            yield scrapy.Request(page, callback=self.parse_page)
            page = page[:-1]

    def parse_page(self, response):
        start_url = 'https://store.steampowered.com/app/'

        for url in response.xpath('//a'):
            found_id = re.findall('/app/(.*?)/', url.extract())
            if found_id:
                game_id = found_id[0]
                game_url = start_url + str(game_id)
                yield scrapy.Request(game_url, callback=self.parse_game)

    def parse_game(self, response):
        item = SteamcoderItem()

        name = response.xpath('//title/text()').extract()
        item['name'] = name[0]

        categories = response.xpath('//*[@class="blockbg"]/a/text()').extract()
        categories = categories[1:]
        item['categories'] = categories

        summary = response.xpath('//*[@class="summary_section"]/span/text()').extract()
        if len(summary) >= 2:
            summary = summary[:2]
            reviews = str(summary[1])
            reviews = reviews[1:-1]
            summary[1] = reviews
            item['summary'] = summary
        if len(summary) == 0:
            item['summary'] = 'No summary'

        release_date = response.xpath('//*[@class="release_date"]/*[@class="date"]/text()').extract()
        item['release_date'] = release_date

        developers = response.xpath('//*[@class="dev_row"]/*[@id="developers_list"]/a/text()').extract()
        item['developers'] = developers

        tags = response.xpath('//*[@class="glance_tags_ctn popular_tags_ctn"]'
                              '/*[@class="glance_tags popular_tags"]/a/text()').extract()

        for i in range(0, len(tags)):
            tag = " ".join(tags[i].split())
            tags[i] = tag
        item['tags'] = tags

        price = response.xpath('//*[@class="game_purchase_action"]/*[@class="game_purchase_action_bg"]'
                               '/*[@class="game_purchase_price price"]/text()').extract()

        for i in range(0, len(price)):
            p = " ".join(price[i].split())
            price[i] = p

        item['price'] = price

        platforms = ['Windows']
        mac = response.xpath('//*[@class="game_page_autocollapse sys_req"]'
                                 '/*[@class="sysreq_tabs"]/*[@data-os="mac"]/text()').extract()
        linux = response.xpath('//*[@class="game_page_autocollapse sys_req"]'
                                 '/*[@class="sysreq_tabs"]/*[@data-os="linux"]/text()').extract()
        if mac:
            platforms.append('macOS')
        if linux:
            platforms.append('SteamOS + Linux')

        item['platforms'] = platforms
        if (not release_date):
           yield item
        else:
            date = release_date[0]
            year = date[-4:]
            if year.isdigit():
                if int(year) > 2000:
                    yield item