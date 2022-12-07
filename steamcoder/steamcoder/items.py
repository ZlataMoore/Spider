# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Compose, Join, MapCompose, TakeFirst

class StripText:
    def __init__(self, chars=' \r\t\n'):
        self.chars = chars

    def __call__(self, value):
        try:
            return value.strip(self.chars)
        except:  # noqa E722
            return value


class SteamcoderItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    categories = scrapy.Field()
    summary = scrapy.Field()
    release_date = scrapy.Field()
    developers = scrapy.Field()
    tags = scrapy.Field()
    price = scrapy.Field()
    platforms = scrapy.Field()




