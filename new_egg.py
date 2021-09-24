#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/7/22 16:43
# @Author : 闫旭浩
# @Email : 874591940@qq.com
# @desc : 新蛋网数据爬取
import re
import threading
import time
from threading import Thread, Lock

from MyUtils import ChromeDriver, ReadExcel, WriteExcel, read_ini

import tkinter
import tkinter.messagebox

# 爬取总量
all_total = 0
# 爬取的次数
spider_index = 1
# 存放商品url
goods_url_list = []
# 线程锁
my_lock = Lock()
# 获取商品url的线程，获取商品详细信息的线程
thread_list = []
# excel写入对象
excel = None
# 已爬取的链接列表
exists_url = []
# ip被禁
human_title = 'Are you a human?'
# 当前爬取到的链接总量
total = 0
# 当前已经成功爬取到数据的总量
spider_total = 0


class Page(ChromeDriver):
    def __init__(self, config):
        super().__init__(headless=config['show_flag'])
        self.config = config

    def get_excel_data(self):
        """
        从excel获取需要爬取的店铺链接
        :return:
        """
        return ReadExcel(self.config['url_excel_path'], sheet_name=self.config['url_sheet_name']).read_col()

    def get_all_goods_url(self, base_url):
        """
        获取该店铺的所有商品链接
        :param base_url: 店铺链接
        :return:
        """
        # 打开链接
        self.chrome.get(base_url)
        page = 1
        max_page = 1
        while page <= max_page:
            # self.chrome.get(base_url + '&page={}'.format(current_page))
            ###########################################
            if human_title in self.chrome.title:
                time.sleep(60)
                # return False
            ###########################################
            # 获取当前页面的所有商品链接
            try:
                a_list = self.get_elements_attribute('//div[@class="item-cell"]/div/a', 'href')
            except:
                a_list = []
            global goods_url_list, spider_total
            a_list = list(set(a_list).difference(set(exists_url)))
            # 添加到待爬取列表中
            goods_url_list.extend(a_list)
            # 待爬取数量+1
            spider_total += len(a_list)
            print('第{}页共获取到{}个链接，目前共获取{}个链接'.format(page, len(a_list), spider_total))
            if max_page == 1:
                try:
                    max_page = self.chrome.find_element_by_xpath(
                        '//div[@class="row has-side-left"]//div[@class="list-wrap"]/div[3]/div/div/div[last()-1]').text
                    max_page = int(max_page.strip())
                except:
                    max_page = 1
            # 下一页
            if max_page != 1:
                try:
                    # 获取页码元素
                    next_btn = self.get_elements(
                        '//div[@class="row has-side-left"]//div[@class="list-wrap"]/div[3]//button')[-1]
                    # 已经到末尾了
                    if next_btn.get_attribute('disabled'):
                        break
                    # 点击下一页
                    self.click_element_by_js(next_btn)
                except:
                    break
            page += 1
        return True

    def run(self):
        """
        启动
        :return:
        """
        shop_ulr_list = self.get_excel_data()
        for shop_url in shop_ulr_list:
            if self.get_all_goods_url(shop_url) == 0:
                break

    def __del__(self):
        print('待爬取的总量为：{}'.format(spider_total))


class Details(ChromeDriver):
    def __init__(self, config):
        # debugger_address_info={'host': '127.0.0.1', 'port': 9222}
        super(Details, self).__init__(headless=config['show_flag'])

    def get_goods_info(self, url):
        """
        获取商品详情页信息
        :param url: 商品链接
        :return:
        """
        # 打开链接
        self.chrome.get(url)
        ###########################################
        retry_num = 0
        while retry_num < 3:
            if human_title in self.chrome.title:
                time.sleep(5)
                self.chrome.refresh()
                time.sleep(5)
                retry_num += 1
            else:
                break
        ###########################################
        # 需要写入excel的数据
        data = ['' for x in range(123)]
        try:
            # 面板div
            div_list = self.get_elements('//*[@id="product-details"]/div[1]/div')
            div_text_list = [x.text for x in div_list]
            # 商品链接                        0   D
            data[0] = self.chrome.current_url
            # 商品编号                        3   D
            data[3] = self.get_element_text('//ol[@class="breadcrumb"]/li[last()]/em')
            # 标题                           5   F
            data[5] = self.get_element_text('//h1')
        except:
            div_list = []
            div_text_list = []
        # 产品说明（字符不超过4000）       6   G
        try:
            data[6] = self.get_element_text('//div[@class="product-bullets"]')
        except:
            pass
        # 产品描述（字符不超过4000）       7   H
        try:
            # 获取 Overview 元素位置
            overview_index = div_text_list.index('Overview')
            # 滑到该元素位置
            self.scroll_to_element_by_js(div_list[overview_index])
            # 点击该栏目
            try:
                self.click_element_by_js(div_list[overview_index])
                time.sleep(1)
            except:
                pass
            # 商品详情
            try:
                product_overview = self.get_element_text('//div[@id="product-overview"]')
            except:
                product_overview = ''
        except:
            product_overview = ''
        data[7] = product_overview
        # 新旧（空就是新）                13  N
        # 可选值：New、Refurbished、UsedLikeNew、UsedVeryGood、UsedGood、UsedAcceptable
        try:
            condition = self.get_element_text('//div[@class="product-condition"]/strong')
            condition_info = {
                'default': 'New',
                'REFURBISHED': 'Refurbished',
                'Used - Like New': 'UsedLikeNew',
                'Used - Very Good': 'UsedVeryGood',
                'Used - Good': 'UsedGood',
                'Used - Acceptable': 'UsedAcceptable',
            }
            condition = condition_info.get(condition, condition_info['default'])
        except:
            condition = 'New'
        data[13] = condition
        # 价格+邮费总价                  20  U
        try:
            # 价格
            price = self.get_element_text(
                '//div[@class="product-pane"]/div[@class="product-price"]//li[@class="price-current"]')
            price = float(price.replace('$', '').replace(',', '')) if price != '' else 0
        except:
            price = 0
        try:
            # 邮费
            send_price = self.chrome.find_element_by_xpath(
                '//div[@class="product-pane"]/div[@class="product-price"]//li[@class="price-ship"]').text
            # 获取邮费的数字部分
            send_price = re.match('^\$(\d+\.\d+)', send_price)
            send_price = float(send_price.group().replace('$', '')) if send_price else 0
        except:
            send_price = 0
        data[20] = price + send_price
        data[21] = send_price
        # 图片用英文,分隔                26  AA
        try:
            image_list = self.get_elements_attribute('//div[@class="swiper-slide"]/div/img', 'src')
            data[26] = ',\n'.join(image_list[:7]) if len(image_list) != 1 else image_list[0]
        except:
            pass
        # 规格说明（不用分开）            36  AK
        try:
            # 获取 Specs 元素位置
            specs_index = div_text_list.index('Specs')
            # 滑到该元素位置
            self.scroll_to_element_by_js(div_list[specs_index])
            # 点击该栏目
            try:
                self.click_element_by_js(div_list[specs_index])
                time.sleep(1)
            except:
                pass
            # key和value
            keys = self.get_elements_text('//table[@class="table-horizontal"]//th')
            values = self.get_elements_text('//table[@class="table-horizontal"]//td')
            specs = []
            for i in range(min(len(keys), len(values))):
                specs.append('{}:{}'.format(keys[i], values[i]))
            specs_str = '\n'.join(specs)
        except:
            specs_str = ''
        data[36] = specs_str.strip()
        ######################
        # '>'.join(self.get_elements_text_by_xpath('//ol[@class="breadcrumb"]/li[position()<last()]')),  # 类目
        ######################
        ##########################################################################
        # 如果获取到的价格为0 data[20] == 0

        # 添加到购物车

        # 获取价格

        # 更新价格

        ##########################################################################

        ################################
        # 如果标题为空，则表示数据爬取失败，则不写入excel
        ################################
        if data[5] == '':
            # 将本链接还插入到待爬取链接中
            my_lock.acquire()
            global goods_url_list
            if url not in goods_url_list:
                goods_url_list.append(url)
            my_lock.release()
            return False
        ################################
        try:
            global excel, total, all_total
            my_lock.acquire()
            # 写入excel
            excel.append_data(data)
            # 已爬取数量+1
            total += 1
            all_total += 1
            my_lock.release()
            # print('本次共{}个，已爬取{}个，爬取总量为：{}，爬取到的数据为：{}'.format(spider_total, total,all_total, data))
            print('第{}次运行，本次需要爬取{}个，目前已爬取{}个，剩余待爬取为{}个。爬取总量为：{}'.format(spider_index, spider_total, total, spider_total - total, all_total))
            return True
        except:
            if my_lock.locked():
                my_lock.release()
        ########################################

    def run(self):
        while True:
            global goods_url_list, exists_url
            try:
                # 页码列表为0，页码线程已启动且页码线程已结束
                if len(goods_url_list) == 0:
                    if thread_list[0] and not thread_list[0].is_alive():
                        break
                    else:
                        time.sleep(1)
                        continue
                url = None
                #####################################################
                # 获取锁
                my_lock.acquire()
                if len(goods_url_list) > 0:
                    # 获取商品链接
                    url = goods_url_list.pop()
                    # exists_url.append(url)
                # 释放锁
                my_lock.release()
                #####################################################
                if not url:
                    continue
                if self.get_goods_info(url):
                    my_lock.acquire()
                    exists_url.append(url)
                    my_lock.release()
            except:
                if my_lock.locked():
                    my_lock.release()


def run():
    global excel, exists_url, total, spider_total
    # 当前爬取到的链接总量
    total = 0
    # 当前已经成功爬取到数据的总量
    spider_total = 0
    config = read_ini('./config.ini')
    config['show_flag'] = True if config['show_flag'] == '1' else False
    # 获取excel写入对象、已爬取的链接
    excel = WriteExcel(config['excel_save_path'], sheet_name=config['excel_sheet_name'])
    exists_url = ReadExcel(config['excel_save_path'], sheet_name=config['excel_sheet_name']).read_col()
    # 创建线程
    global thread_list
    thread_list = [Thread(target=Page(config).run)]
    for num in range(config['thread_num']):
        thread_list.append(Thread(target=Details(config).run))
    print('正在启动线程！')
    # 启动线程
    for t in thread_list:
        t.start()
    print('线程启动完毕！')
    # 阻塞
    for t in thread_list:
        t.join()
    print('线程运行完毕！')


if __name__ == '__main__':
    while True:
        print('正在进行第{}次爬取'.format(spider_index))
        run()
        # 爬取完毕
        if spider_total == total:
            break
        spider_index += 1
    root = tkinter.Tk()
    root.wm_attributes('-topmost', 1)
    tkinter.messagebox.showinfo('提示', '运行结束，共爬取到{}条数据！'.format(all_total))
    # pyinstall -F new_egg.py
