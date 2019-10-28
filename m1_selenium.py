import boto3
# sudo apt-get install libfontconfig
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import pandas as pd
import os
import datetime
script_dir = os.path.dirname(__file__)
rel_path = "phantomjs-2.1.1-linux-x86_64/bin/phantomjs"
phantomjs_path = os.path.join(script_dir, rel_path)
# phantomjs_path='/phantomjs-2.1.1-macosx/bin/phantomjs'

key_id = ''
secret_access_key = ''


def table():
    '''
    Connect to AWS via boto3 and return table
    :return: AWS object
    '''
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id=key_id, aws_secret_access_key=secret_access_key)
    table = dynamodb.Table('lookupbyupc')
    return table


def getPhantomJsWebDriver():
    while True:
        try:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36')
            service_args = []
            service_args.append('--proxy-type=http')
            service_args.append('--load-images=no')
            driver = webdriver.PhantomJS(phantomjs_path, desired_capabilities=dcap, service_args=service_args)
            driver.set_page_load_timeout(10)
            driver.set_script_timeout(10)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            print('getPhantomJsWebDrive:'+str(e))
            continue


def try_or(fn, default):
    try:
        return fn()
    except:
        return default


def getAmazonInfoFromUPC(ItemUpc):
    try:
        awstable = table()
        Adriver = getPhantomJsWebDriver()
        AmazonUrl = "https://www.amazon.com/ref=nav_logo"
        Adriver.get(AmazonUrl)
        search = Adriver.find_element_by_xpath('//*[@id="twotabsearchtextbox"]')
        search.send_keys(ItemUpc)
        search.submit()
        print ('Amazon Search Page: '+Adriver.current_url)
        Adriver.get(Adriver.current_url)
        # time.sleep(1)
        axpath = '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div[1]/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a'
        Adriver.find_element_by_xpath(axpath).click()
        # time.sleep(2)
        print('Item url: '+Adriver.current_url)
        ItemName = Adriver.find_element_by_xpath('//*[@id="productTitle"]').text
        ItemSalePrice =try_or(lambda: Adriver.find_element_by_xpath('//*[@id="priceblock_ourprice"]').text.strip('$'), 'NaN')
        Ingredients = try_or(lambda: Adriver.find_element_by_xpath('//*[@id="important-information"]/div[1]/p').text.strip('\t'), 'NaN')
        ReviewStars = try_or(lambda: Adriver.find_element_by_xpath('//*[@id="reviewsMedley"]/div/div[1]/div[2]/div[1]/div/div[2]/div/span/span/a/span').text.split()[0], 'NaN')
        ProductDimension = try_or(lambda: Adriver.find_element_by_xpath('//*[@id="detail-bullets"]/table/tbody/tr/td/div/ul/li[1]').text.strip('\t'), 'NaN')
        productInfo =try_or(lambda: Adriver.find_element_by_xpath('//*[@id="productDescription"]/p').text, 'NaN')
        ReviewNumber = try_or(lambda: Adriver.find_element_by_xpath('//*[@id="acrCustomerReviewText"]').text.split()[0], 'NaN')
        ASIN = try_or(lambda: Adriver.current_url.split('/')[5], 'NaN')
        if productInfo == '':
            productInfo = 'NaN'
        # Item = {
        # 'upc': ItemUpc[0],
        # 'Name': ItemName,
        # 'Price': ItemSalePrice,
        # 'Ingredients': Ingredients,
        # 'Review Star': ReviewStars,
        # 'Review Number': ReviewNumber,
        # 'Product Info': productInfo,
        # 'Product Dimension': ProductDimension,
        # 'ASIN': Adriver.current_url.split('/')[5],
        # 'URL': Adriver.current_url
        # }
        if ItemName is not None:
            try:
                awstable.put_item(
                    Item={
                        'upc': ItemUpc[0],
                        'ASIN': ASIN,
                        'Name': ItemName,
                        'Price': ItemSalePrice,
                        'Ingredients': Ingredients,
                        'Review Star': ReviewStars,
                        'Review Number': ReviewNumber,
                        'Product Info': productInfo,
                        'Product Dimension': ProductDimension,
                        'URL': Adriver.current_url,
			             'Time': datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
                        })
            except Exception as e:
                print('put_item:'+str(e))
        Adriver.close()
    except Exception as e:
        print('getAmazonInfoFromUPC'+str(e))


def lambda_handler(event, context):
    UPC_Path = 'upc_0.csv'
    upc_list = pd.read_csv(UPC_Path, dtype=str, header=None)
    for upc in upc_list.values.tolist():
        getAmazonInfoFromUPC(upc)
    # random_keyward = upc_list[random, randit(0, len(upc_list)-1)]
    # pprint.pprint('Pulling data for {}'.format(random_keyward))


if __name__ == "__main__":
    lambda_handler(None, None)




