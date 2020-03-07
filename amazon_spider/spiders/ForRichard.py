# -*- coding: utf-8 -*-
import time
import re
import os
import scrapy
from bs4 import BeautifulSoup
import configparser
from amazon_spider.items import AmazonSpiderItem



class ForrichardSpider(scrapy.Spider):
    name = 'ForRichard'
    allowed_domains = ['amazon']
    start_urls = ['http://amazon/']
    url = "https://www.amazon.com/s?k=pen&page=1&qid=1582024299&ref=sr_pg_1"
    url1 = "https://www.amazon.com/s?k="
    url2 = "&page="
    url3 = "&ref=sr_pg_"
    search = "pen"

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36",
    }
    str_cookie = ""
    cookie =''

    pick_num = 0
    pick_num_max = 100
    page_num = 1
    page_num_max = 0
    pick_table = []
    url_item_table = []
    url_item_num = 0

    #def __init__(self, key=None, num=None, *args, **kwargs):
    def __init__(self,  *args, **kwargs):

        if os.path.exists('ForRichard.cfg'):
            fp = configparser.ConfigParser()
            fp.read('ForRichard.cfg')
            sec = fp.sections()

            self.search = fp.get("Richard", "key")
            self.pick_num_max = fp.getint("Richard", "num")
            self.headers['User-Agent'] = fp.get("Richard", "ua")
            self.site = fp.get('Richard', 'site')
            self.url1 = 'https://www.amazon.' + self.site + '/s?k='
            if self.site == 'com':
                self.str_cookie = fp.get("Richard", "cookie_usa")
            elif self.site == 'co.uk':
                self.str_cookie = fp.get("Richard", 'cookie_uk')
        super(eval(self.__class__.__name__), self).__init__(*args, **kwargs)


    def page_num_max_judge(self, soup):

        if self.page_num_max == 0:
            page_max = soup.find('ul', class_='a-pagination')
            print(page_max.prettify())
            page_num_list = page_max.find_all('li')
            self.page_num_max = int(page_num_list[-2].get_text())

    def start_requests(self):
        """
        重载start_requests方法 待登录成功后，再进入parse进行数据爬取
        """
        print(self.pick_num_max)
        print(self.search)
        self.cookie = {i.split('=')[0]: i.split('=')[1] for i in self.str_cookie.split('; ')}
        url_search =self.url1 + self.search + self.url2 + str(self.page_num) + self.url3 + str(self.page_num)
        return [scrapy.Request(url_search, headers=self.headers, cookies=self.cookie, callback=self.parse)]

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        area = soup.find('span', attrs={'class': 'nav-line-2', 'id': 'glow-ingress-line2'})
        if area is not None:
            temp = area.get_text()
            if 'New York' in temp:
                print('area is NewYork')
            elif 'Wakefield' in temp:
                print('area is UK')
            elif 'China' in temp:
                print('area is China, Is your cookie overdue?')
            elif '540-8570' in temp:
                print('area is Japan')

        #注意，因为这个商品列表是第二个div class s-result-list s-search-results sg-row
        if self.page_num_max == 0:
            page_max = soup.find('ul', class_='a-pagination')
            #print(page_max.prettify())
            page_num_list = page_max.find_all('li')
            self.page_num_max = int(page_num_list[-2].get_text())

        for tb in soup.find_all('div', class_='s-result-list s-search-results sg-row'):
            # 这里是搜索的商品列表
            #print(tb)
            for link in tb.find_all(lambda tb: tb.has_attr('data-asin') and tb.has_attr('data-index')):
                # print(link.prettify())
                # 如果data-asin是空，那么则跳过
                if not link.attrs['data-asin'].strip():
                    continue
                # 这里是每个商品的处理现场
                pick_single = {'data_asin': link.attrs['data-asin'], 'name': 'x', 'price_1': 'x', 'price_2': 'y',
                               'starts': 'x', 'timeget': 'x'}
                # 商品名称
                item = link.find('span', class_='a-text-normal')
                pick_single['name'] = item.get_text()
                # 价格
                price_num = 0
                for price in link.find_all('span', class_='a-offscreen'):
                    if price_num == 0 and price is not None:
                        pick_single['price_1'] = price.get_text()
                    if price_num == 1 and price is not None:
                        pick_single['price_2'] = price.get_text()
                    price_num += 1
                # 星级
                starts = link.find('span', class_='a-icon-alt')
                if starts is not None:
                    pick_single['starts'] = starts.get_text()
                # 最快到货日期
                aa = link.find('span', attrs={'class': 'a-text-bold', 'dir': 'auto'})
                if aa is not None:
                    pick_single['timeget'] = aa.get_text()

                self.pick_table.append(pick_single)
                # 商品数量+1
                self.pick_num += 1
                if self.pick_num == self.pick_num_max:
                    yield self.parse_midware(self)
                    return 0
        self.page_num += 1
        if self.page_num <= self.page_num_max:
             next_page = self.url1 + self.search + self.url2 + str(self.page_num) + self.url3 + str(self.page_num)
             yield scrapy.Request(next_page, headers=self.headers, cookies=self.cookie,
                                  callback=self.parse,  dont_filter=True)

    def parse_midware(self, response):

        for pd in self.pick_table:
            url_aditional = 'https://www.amazon.' + self.site + '/dp/' + pd['data_asin']
            # 'B004QHI43S'
            self.url_item_table.append(url_aditional)

        #print(self.url_item_table[0])
        return scrapy.Request(self.url_item_table[self.url_item_num], headers=self.headers, cookies=self.cookie,
                              callback=self.parse_aditional, dont_filter=True)

    def parse_aditional(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        #print(soup.prettify())
        amazonItem = AmazonSpiderItem()
        amazonItem['Name'] = self.pick_table[self.url_item_num]['name']
        amazonItem['Asin'] = self.pick_table[self.url_item_num]['data_asin']
        amazonItem['Price_Sale'] = self.pick_table[self.url_item_num]['price_1']
        amazonItem['Price_List'] = self.pick_table[self.url_item_num]['price_2']
        amazonItem['Stars'] = self.pick_table[self.url_item_num]['starts']
        amazonItem['getTime'] = self.pick_table[self.url_item_num]['timeget']
        amazonItem['DateAvailable'] = ''
        amazonItem['Variants'] = ''
        amazonItem['Ratings'] = ''
        amazonItem['Weight'] = ''
        amazonItem['BSR_Parent'] = ''
        amazonItem['BSR_Child'] = ''
        amazonItem['QA'] = ''
        #变体 填写
        tag_variant = soup.find('span', class_="selection")
        if tag_variant is not None:
            str_var = tag_variant.get_text()
            str_var = str_var.replace("\n", " ")
            amazonItem['Variants'] = str_var.strip()
        #rating 填写
        ratings = soup.find('span', attrs={'id': 'acrCustomerReviewText'})
        if ratings is not None:
            amazonItem['Ratings'] = ratings.get_text()
        AqBig = soup.find('a', attrs={'id': 'askATFLink'})
        if AqBig is not None:
            str_aq = (AqBig.find('span')).get_text()
            str_aq = str_aq.replace("\n", " ")
            amazonItem['QA'] = str_aq.strip()

        if self.site == 'co.uk':
            t_uk = soup.find('table', attrs={'cellpadding': '0', 'cellspacing': '0', 'id':'productDetailsTable'})
            if t_uk is not None:
                #print(t_uk.prettify())
                for tr_uk in t_uk.find_all('tr'):

                    td_uk = tr_uk.find('td')
                    if td_uk['class'] == ['bucket']:
                        ## 这就是比较少的那张表格
                        for li_uk in td_uk.find_all('li'):
                            b_uk = li_uk.find('b')
                            if b_uk is not None:
                                b_item = b_uk.get_text()
                                if 'available' in b_item:
                                    p = li_uk.get_text()
                                    amazonItem['DateAvailable'] = p[p.find(":")+1:]
                                elif 'Weight' in b_item:
                                    p = li_uk.get_text()
                                    amazonItem['Weight'] = p[p.find(":")+1:]
                                elif 'Bestsellers' in b_item:
                                    amazonItem['BSR_Parent'] = b_uk.next_sibling.strip()
                                    li_bsr_uk = li_uk.find('ul', attrs={'class': 'zg_hrsr'})
                                    li_bsr_uk_str = li_bsr_uk.get_text()
                                    li_bsr_uk_str = li_bsr_uk_str.replace("\n", " ")
                                    amazonItem['BSR_Child'] = li_bsr_uk_str.strip()
            t_fst = soup.find('div', attrs={'id': 'prodDetails'})
            if t_fst is not None:
                t_second = t_fst.find('div', attrs={'class': 'column col2 '})
                t_uk = t_second.find('table', attrs={'cellpadding': '0', 'cellspacing': '0'})
                if t_uk is not None:
                    for tr_uk in t_uk.find_all('tr'):
                        td_uk = tr_uk.find('td')
                        item_key = td_uk.get_text()

                        if 'Shipping Weight' in item_key:
                            td_next_uk = td_uk.find_next_sibling()
                            item_value = td_next_uk.get_text()
                            str_we = item_value.replace("\n", " ")
                            amazonItem['Weight'] = str_we.strip()

                        elif 'Amazon Bestsellers Rank' in item_key:
                            td_next_uk = td_uk.find_next_sibling()
                            a_uk = td_next_uk.find('a')
                            amazonItem['BSR_Parent'] = a_uk.previous_sibling.strip()
                            li_uk = td_next_uk.find('li')
                            str_bsr = li_uk.get_text()
                            str_bsr = str_bsr.replace("\n", " ")
                            amazonItem['BSR_Child'] = str_bsr.strip()

                        elif 'vailable' in item_key:
                            td_next_uk = td_uk.find_next_sibling()
                            item_value = td_next_uk.get_text()
                            str_date = item_value
                            str_date = str_date.replace("\n", " ")
                            amazonItem['DateAvailable'] = str_date.strip()




        elif self.site == 'com':
            tpro = soup.find('div', attrs={'id': 'prodDetails', 'class': 'a-section'})
            if tpro is not None:
                tb = tpro.find('div', attrs={'id': 'productDetails_db_sections'})
                #aq 填写
                if tb is not None:

                    for tr in tb.find_all('tr'):
                        th = tr.find('th')
                        item = th.get_text()

                        # if 'Customer Reviews' in item:
                        #     ratings = tr.find('span', attrs={'id': 'acrCustomerReviewText'})
                        #     amazonItem['Ratings'] = ratings.get_text()
                        if 'Shipping Weight' in item:
                            weight = tr.find('td')

                            str_we = weight.get_text()
                            str_we = str_we.replace("\n", " ")
                            amazonItem['Weight'] = str_we.strip()
                        elif 'Best Sellers Rank' in item:
                            bsr_num = 0
                            for bsr in tr.find_all('span'):
                                if bsr_num == 1:
                                    str_bsr = bsr.get_text()
                                    str_bsr = str_bsr.replace("\n", " ")
                                    amazonItem['BSR_Parent'] = str_bsr.strip()
                                if bsr_num == 2:
                                    str_bsr = bsr.get_text()
                                    str_bsr = str_bsr.replace("\n", " ")
                                    amazonItem['BSR_Child'] = str_bsr.strip()
                                bsr_num += 1
                        elif 'Date First' in item:
                            date_avaible = tr.find('td')
                            str_date = date_avaible.get_text()
                            str_date = str_date.replace("\n", " ")
                            amazonItem['DateAvailable'] = str_date.strip()

                else:
                    tb1 = tpro.find('table', attrs={'id': 'productDetails_detailBullets_sections1'})
                    if tb1 is not None:
                        for tr1 in tb1.find_all('tr'):
                            th1 = tr1.find('th')
                            item = th1.get_text()
                            if 'Shipping Weight' in item:
                                weight = tr1.find('td')

                                str_we = weight.get_text()
                                str_we = str_we.replace("\n", " ")
                                amazonItem['Weight'] = str_we.strip()
                            elif 'Best Sellers Rank' in item:
                                bsr_num = 0
                                for bsr in tr1.find_all('span'):
                                    if bsr_num == 0:
                                        str_bsr = bsr.get_text()
                                        str_bsr = str_bsr.replace("\n", " ")
                                        amazonItem['BSR_Parent'] = str_bsr.strip()
                                    if bsr_num == 1:
                                        str_bsr = bsr.get_text()
                                        str_bsr = str_bsr.replace("\n", " ")
                                        amazonItem['BSR_Child'] = str_bsr.strip()
                                    bsr_num += 1
                            elif 'Date First' in item:
                                    date_avaible = tr1.find('td')
                                    str_date = date_avaible.get_text()
                                    str_date = str_date.replace("\n", " ")
                                    amazonItem['DateAvailable'] = str_date.strip()
                    # else 后续添加动态添加条目的方法
        yield amazonItem
        self.url_item_num += 1
        print('finish crawl the {} page'.format(self.url_item_num))
        if self.url_item_num < len(self.url_item_table):
            yield scrapy.Request(self.url_item_table[self.url_item_num], headers=self.headers, cookies=self.cookie,
                                 callback=self.parse_aditional,  dont_filter=True)



