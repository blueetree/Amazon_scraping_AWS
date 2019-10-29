# -*- coding: utf-8 -*-

from scrapy import signals
import boto3

key_id = ''
secret_access_key = ''
region_name = ''
table_name = ''

class AmazonPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        db = boto3.resource(
            'dynamodb',
            aws_access_key_id=key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )
        self.table = db.Table(table_name)

    def spider_closed(self, spider):
        self.table = None

    def process_item(self, item, spider):
        self.table.put_item(
            TableName=table_name,
            Item={k: v for k, v in item.items()}
        )
        return item
