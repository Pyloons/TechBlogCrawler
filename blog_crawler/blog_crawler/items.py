# -*- coding: utf-8 -*-

import scrapy


class CSDNArticleItem(scrapy.Item):
    id = scrapy.Field()
    crawled_time = scrapy.Field()
    username = scrapy.Field()
    title = scrapy.Field()
    publish_time = scrapy.Field()
    readed = scrapy.Field()
    detail = scrapy.Field()
    comments_num = scrapy.Field()
    stars = scrapy.Field()

class CSDNAuthorItem(scrapy.Item):
    username = scrapy.Field()
    crawled_time = scrapy.Field()
    nickname = scrapy.Field()
    raws_num = scrapy.Field()
    fans_num = scrapy.Field()
    like_to_num = scrapy.Field()
    gen_comments_num = scrapy.Field()
    visit_num = scrapy.Field()
    points = scrapy.Field()
    rank = scrapy.Field()
