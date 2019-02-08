# -*- coding:utf-8 -*-

"""豆瓣读书记录爬虫(未完成)"""

import time
import queue

import requests
from bs4 import BeautifulSoup


class DoubanBookSpider(object):
    def __init__(self):
        self.url = None
        self.headers = {
            "User-Agent" : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6)',
            "Cookie" : 'gr_user_id=86b0c2b8-5f81-493a-9cbf-7725c51d1339; _ga=GA1.2.504479495.1478321454; _vwo_uuid_v2=FB5106C8C68355E51DC13B7B70533F92|afab7b50c2db14009031e2272d0c60a5; push_doumail_num=0; douban-fav-remind=1; douban-profile-remind=1; __utmv=30149280.14596; bid=THNz4PoWvZs; ll="118163"; Hm_lvt_6e5dcf7c287704f738c7febc2283cf0c=1545640847,1545966728; push_noty_num=0; ct=y; __utmc=30149280; __utmz=30149280.1548926241.231.111.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmc=81379588; __utmz=81379588.1548926241.110.99.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); viewed="3283983_1795079_27039522_1088054_25900403_27096665_5333562_10432347_4199741"; dbcl2="145966625:MtAW0GLOZLs"; ck=DSp9; ap_v=0,6.0; __utma=30149280.504479495.1478321454.1548986872.1549074535.233; __utmt=1; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1549074553%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.100001.3ac3=*; __utmt_douban=1; __utma=81379588.504479495.1478321454.1548986884.1549074553.112; _pk_id.100001.3ac3=06b64c4d7715b8cd.1535887699.111.1549074575.1548988085.; __utmb=30149280.4.10.1549074535; __utmb=81379588.2.10.1549074553'
        }

    def process_url(self, value):
        return  "https://book.douban.com/people/145966625/collect?start={}&sort=time&rating=all&filter=all&mode=grid".format(value*15-15)

    def get_page_sum(self):

        response = requests.get(self.process_url(1), headers=self.headers)
        soup = BeautifulSoup(response.content)
        page_sum_node = soup.select("#content > div.grid-16-8.clearfix > div.article > div.paginator > a")
        return int(page_sum_node[-1].text)

    def get_page_urls(self):
        page_sum = self.get_page_sum()

        # page_url_list = []
        # for page_data in range(1, page_sum+1):
        #     page_url_list.append(self.process_url(page_data))
        # print(page_url_list)

        for page_data in range(1, page_sum + 1):
            yield self.process_url(page_data)

    def page_data_spider(self):
        page_data_list = []
        for page_url in self.get_page_urls():
            # page_data_list.append(response.get(page_url, headers=self.headers))
            # time.sleep(3)
            response = response.get(page_url, headers=self.headers)
            if response.status_code == 200:
                pass
            else:
                pass

        for page_data in page_data_list:
            pass





    def parse_book_data(self):
        pass

    @staticmethod
    def main():
        pass

if __name__ == "__main__":
    DoubanBookSpider.main()
    dbs = DoubanBookSpider()
    dbs.page_data_spider()
