# -*- coding: utf-8 -*-
import scrapy
from ..items import UpcScrapyItem
import pandas as pd
import datetime
from scrapy.selector import Selector
import json
import urllib
import csv

def try_or(fn, default):
    try:
        return fn()
    except:
        return default


class LookupbyupcSpider(scrapy.Spider):
    name = 'lookupbyUPC'
    allowed_domains = ['amazon.com']
    start_urls = ['https://www.amazon.com/']

    def start_requests(self):
        UPC_Path = 'upc_2.csv'
        upc_list = pd.read_csv(UPC_Path, dtype=str, header=None)
        for each_upc in upc_list.values.tolist():
            full_url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + str(each_upc[0])
            print(full_url)
            # process.crawl(spider, input='inputargument', first='James', last='Bond')
            # yield self.make_requests_from_url(full_url)
            yield scrapy.Request(full_url, self.parse, meta=dict(upc=str(each_upc[0])))


    def parse(self, response):
        print("response", response.url)
        try:
            sel = Selector(response)
            xpath = '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div[1]/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a/@href'
            item_link = sel.xpath(xpath).extract()[0]
            print('item_link:'+item_link)
            yield scrapy.Request('https://www.amazon.com' + item_link, callback=self.parse_items, meta=dict(upc=response.meta['upc']))
        except Exception as e:
            print('search_list:' + str(e))
            return

    def parse_items(self, response):
        print("entered items", response.url)
        try:
            sel = Selector(response)
            print('sel:'+ str(sel))
            items = UpcScrapyItem()
            ItemName = sel.css('#productTitle').css('::text').extract()
            if ItemName is None:
                return
            ItemSalePrice = try_or(lambda: sel.css('#priceblock_ourprice').css('::text').extract()[0].strip('$'), 'NaN')
            Ingredients = try_or(lambda: sel.css('h2+ .content p').css('::text').extract()[0].strip().replace('\n', ' ').replace('\t', ''), 'NaN')
            ReviewStars = try_or(lambda: sel.css('#reviewsMedley .a-size-medium').css('::text').extract()[0][0], 'NaN')
            ProductDimension = try_or(lambda: ''.join(sel.css('.content > ul li:nth-child(1)').css('::text').extract()).replace('\n', ' ').replace('\t', ''), 'NaN')
            productInfo = try_or(lambda: sel.css('#productDescription p').css('::text').extract()[0].strip().replace('\n', ' ').replace('\t', ''), 'NaN')
            ReviewNumber = try_or(lambda: sel.css('#acrCustomerReviewText').css('::text').extract()[0].split()[0], 'NaN')
            ASIN = try_or(lambda: response.url.split('/')[5], 'NaN')
            if productInfo == '':
                productInfo = 'NaN'
            if ProductDimension == '':
                ProductDimension = 'NaN'
            items['upc'] = response.meta['upc']
            items['ItemName'] = list(map(lambda s: s.strip(), ItemName))[0]
            items['ItemSalePrice'] = ItemSalePrice
            items['Ingredients'] = Ingredients
            items['ReviewStars'] = ReviewStars
            items['ProductDimension'] = ProductDimension
            items['productInfo'] = productInfo
            items['ReviewNumber'] = ReviewNumber
            items['ASIN'] = ASIN
            items['URL'] = response.url
            items['Time'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            yield items
        except Exception as e:
            print('Error_item:' + str(e))
            with open('upc_lost_multi.csv', 'a') as fd:
                fd.write(response.meta['upc'])
                # fd.write(response.url)
                fd.write('\n')
            return
