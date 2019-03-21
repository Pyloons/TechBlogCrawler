# -*- coding: utf-8 -*-
import scrapy, re, time
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider

from pymongo import MongoClient

from blog_crawler.items import CSDNArticleItem, CSDNAuthorItem


class CSDNSpiderSpider(CrawlSpider):
    name = 'csdn_spider'
    allowed_domains = ['blog.csdn.net']
    start_urls = ['https://blog.csdn.net/']
    test_limit = 0
    mgclient = MongoClient('127.0.0.1', 27017)
    csdn_db = mgclient.csdn_blog

    page_pattern = r'.*\.?blog.csdn.net\/.*\/article\/details\/\d+'

    rules = [
        Rule(LinkExtractor(page_pattern), callback='parse_page'),
    ]

    def parse_article(self, response):
        article_item = CSDNArticleItem()
        
        name = re.findall(r'blog.csdn.net\/(.*)\/article', response.url)[0]
        article_raw_id = re.findall(r'details\/(\d+)', response.url)[0]
        article_id = name + '_' + article_raw_id
        article_item['id'] = article_id
        
        article_item['crawled_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        article_item['username'] = name  # 与作者集合的数据项做关联用
        article_item['title'] = response.xpath('//h1[@class="title-article"]/text()').extract_first()
        article_item['publish_time'] = response.xpath('//span[@class="time"]/text()').extract_first()
        article_item['readed'] = int(response.xpath('//span[@class="read-count"]/text()').extract_first()[4:])
        
        detail = response.xpath('string(//div[@id="article_content"])').extract_first()
        detail = re.sub('\n+','\n',detail)
        detail = re.sub(r'\s+',' ',detail)
        article_item['detail'] = detail

        comments_num = response.xpath('//a[contains(@class,"btn-comments")]/p/text()').extract_first().strip()
        if comments_num:
            comments_num = int(comments_num)
        else:
            comments_num = 0
        article_item['comments_num'] = comments_num

        stars = response.xpath('//button[contains(@class,"btn-like")]/p/text()').extract_first().strip()
        if stars:
            stars = int(stars)
        else:
            stars = 0
        article_item['stars'] = stars

        return article_item

    def parse_author(self, response):
        author_item = CSDNAuthorItem()
        name = re.findall(r'blog.csdn.net\/(.*)\/article', response.url)[0]
        author_item['username'] = name
        author_item['crawled_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        author_item['nickname'] = response.xpath('//a[@id="uid"]/text()').extract_first()
        infos = response.xpath('//div[contains(@class,"data-info")]/dl')
        for info in infos:
            got_a_tag = info.xpath('.//dt')[0].xpath('string(.)').extract_first()
            got_a_num = int(info.xpath('.//@title').extract_first())
            if got_a_tag == "原创":
                author_item['raws_num'] = got_a_num
            elif got_a_tag == "粉丝":
                author_item['fans_num'] = got_a_num
            elif got_a_tag == "喜欢":
                author_item['like_to_num'] = got_a_num
            elif got_a_tag == "评论":
                author_item['gen_comments_num'] = got_a_num
        grades = response.xpath('//div[contains(@class,"grade-box")]/dl')
        for grade in grades:
            got_a_tag = grade.xpath('.//dt/text()').extract_first()[:2]
            if got_a_tag == '等级':
                continue

            got_a_num = grade.xpath('.//dd/@title')
            if not got_a_num:
                got_a_num = grade.xpath('.//@title')
            got_a_num = int(got_a_num.extract_first())

            if got_a_tag == '访问':
                author_item['visit_num'] = got_a_num
            elif got_a_tag == '积分':
                author_item['points'] = got_a_num
            elif got_a_tag == '排名':
                author_item['rank'] = got_a_num
        return author_item

    def parse_page(self, response):
        self.test_limit += 1
        if self.test_limit > 10:
            raise CloseSpider('test crawling done')

        # name = re.findall(r'blog.csdn.net\/(.*)\/article', response.url)[0]
        # name = re.findall(r'blog.csdn.net\/(.*)\/article', response.url)[0]
        # article_raw_id = re.findall(r'details\/(\d+)', response.url)[0]
        # article_id = name + '_' + article_raw_id
        # if not self.csdn_db.authors.find_one({'username': name}):
        yield self.parse_author(response)
        yield self.parse_article(response)

        urls_pattern = r'(https\:\/\/.*\.?blog.csdn.net\/.*\/article\/details\/\d+)'
        urls = re.findall(urls_pattern, response.text)
        urls.append(response.url)

        for url in urls:
            # name = re.findall(r'blog.csdn.net\/(.*)\/article', url)[0]
            # article_raw_id = re.findall(r'details\/(\d+)', url)[0]
            # article_id = name + '_' + article_raw_id
            # if not self.csdn_db.articles.find_one('id', article_id):
            yield scrapy.Request(url, callback=self.parse_page)
