# -*- coding: utf-8 -*-
import scrapy
from ..items import UpcScrapyItem
import pandas as pd
import datetime
from scrapy.selector import Selector

def try_or(fn, default):
    try:
        return fn()
    except:
        return default


class LookupbyupcSpider(scrapy.Spider):
    name = 'lookupbyUPC'
    allowed_domains = ['amazon.com']
    start_urls = ['http://amazon.com/']

    def parse(self, response):
        UPC_Path = ''
        upc_list = pd.read_csv(UPC_Path, dtype=str, header=None)
        all_links = []
        for each_upc in upc_list.values.tolist():
            full_url = "http://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + str(each_upc[0])
            print(full_url)
            all_links.append(scrapy.Request(full_url, self.parse_lists, meta=dict(upc=str(each_upc[0]))))
        return all_links


    def parse_lists(self, response):
        print("response", response.url)
        try:
            all_item_links = []
            sel = Selector(response)
            xpath = '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div[1]/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a/@href'
            item_links = sel.xpath(xpath).extract()
            # item_links = sel.css('.index\=0 .a-link-normal.a-text-normal').css('::attr(href)').extract()
            for each_link in item_links:
                print('item_link:'+each_link)
                my_request = scrapy.Request('http://amazon.com' + each_link, callback=self.parse_items, meta=dict(upc=response.meta['upc']))
                all_item_links.append(my_request)

                return all_item_links
        except Exception as e:
            print('search_list:' + str(e))
            return

    def parse_items(self, response):
        print("entered items", response.url)
        try:
            sel = Selector(response)
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
            print('item:' + str(e))
            return
