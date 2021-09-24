#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/7/22 16:43
# @Author : 闫旭浩
# @Email : 874591940@qq.com
# @desc : Selenium下的Chrome对象
import os

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from . import create_proxy_auth_extension


class ChromeDriver(object):
    def __init__(self, executable_path='chromedriver', binary_location=None, wait_time=30, headless=False,
                 no_sandbox=True, max_window=True, window_size=None, fullscreen=False, incognito=False,
                 disable_gpu=True, ignore_errors=True, disable_infobars=True, hide_scroll=True, mute_audio=False,
                 disable_image=False, disable_js=False, disable_java=False,
                 disable_password_alert=True, disable_browser_alert=True, user_agent=None, debugger_address_info=None,
                 chrome_data_path=None, proxy_info=None, auth_proxy_info=None, phone_info=None,
                 lang=None, crx_plugin_list=None):
        """
        初始化参数，打开浏览器
        :param executable_path: str chromedriver路径
        :param wait_time: int 浏览器等待超时时间
        :param headless: True | False 无头浏览器
        :param no_sandbox: True | False 以最高权限运行
        :param max_window: True | False 是否最大化
        :param window_size: True | False 指定窗口大小
        :param fullscreen: True | False 是否全屏
        :param incognito: True | False 是否无痕
        :param disable_gpu: True | False 是否禁用GPU加速
        :param ignore_errors: True | False 是否忽略证书错误
        :param disable_infobars: True | False 在窗口上不出现‘自动化测试’提示
        :param hide_scroll: True | False 是否不显示滚动条
        :param mute_audio: True | False 是否静音
        :param disable_image: True | False 是否不显示图片
        :param disable_js: True | False 是否禁用js
        :param disable_java: True | False 是否禁用java
        :param disable_password_alert: True | False 禁止弹出密码提示框
        :param disable_browser_alert: True | False 禁止浏览器弹窗
        :param hide_scroll: True | False 是否隐藏滚动条
        :param user_agent: str 设置请求头
        :param debugger_address_info: dict 监听地址和端口号。参数值样例：{'host': '127.0.0.1', 'port': 9222}
        :param chrome_data_path: str  Chrome数据保存路径
        :param proxy_info: dict 代理信息。
        :param phone_info: dict 页面显示移动端。参数值样例：{'deviceName': 'iPhone 6/7/8'}
        :param lang: str 语言
        :param crx_plugin_list: list 插件列表
        """
        self.proxy_plugin_path = None
        options = ChromeOptions()
        # 接管已打开的浏览器
        if debugger_address_info:
            # chrome.exe --remote-debugging-port=9222
            options.add_experimental_option('debuggerAddress', "{host}:{port}".format(**debugger_address_info))
        else:
            # 指定浏览器位置
            if binary_location:
                options.binary_location = binary_location
            # 无头浏览器
            if headless:
                options.add_argument('--headless')
            # 以最高权限运行
            if no_sandbox:
                options.add_argument('--no-sandbox')
            # 最大化
            if max_window:
                options.add_argument('--start-maximized')
            # 指定窗口大小
            if window_size:
                options.add_argument('window-size={width}x{height}'.format(**window_size))
            # 浏览器全屏
            if fullscreen:
                options.add_argument('--start-fullscreen')
            # 无痕浏览
            if incognito:
                options.add_argument('--incognito')
            # 禁用GPU加速
            if disable_gpu:
                options.add_argument('--disable-gpu')
            # 忽略证书错误
            if ignore_errors:
                options.add_argument('--ignore-certificate-errors')
            # 在窗口上不出现‘自动化测试’提示
            if disable_infobars:
                # 方法一：可能会无效
                options.add_argument('--disable-infobars')
                # 方法二：设置开发者模式启动，该模式下webdriver属性为正常值
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
            # 隐藏滚动条, 应对一些特殊页面
            if hide_scroll:
                options.add_argument('--hide-scrollbars')
            # 用户数据位置
            if chrome_data_path:
                # chrome.exe --user-data-dir="......"
                options.add_argument(r'--user-data-dir={}'.format(chrome_data_path))
            # 代理
            if proxy_info:
                proxy = '{host}:{port}'.format(**proxy_info)
                if proxy_info.get('scheme'):
                    proxy = proxy_info.get('scheme') + '://' + proxy
                options.add_argument('--proxy-server={}'.format(proxy))
            if auth_proxy_info:
                self.proxy_plugin_path = create_proxy_auth_extension(**auth_proxy_info)
                options.add_extension(self.proxy_plugin_path)
            # 语言
            if lang:
                options.add_argument('--lang={}'.format(lang))
            # 添加UA
            if user_agent:
                options.add_argument('user-agent="{}"'.format(user_agent))
            # 切换到手机页面
            if phone_info:
                options.add_experimental_option('mobileEmulation', phone_info)
            # 浏览器静音
            if mute_audio:
                options.add_argument("--mute-audio")
            # 不加载图片,提升速度
            if disable_image:
                # 方法一：
                options.add_argument('blink-settings=imagesEnabled=false')
                # 方法二：
                # prefs = {"profile.managed_default_content_settings.images": 2}
                # options.add_experimental_option('prefs", prefs)
            # 禁用JavaScript
            if disable_js:
                options.add_argument('--disable-javascript')
            if disable_java:
                options.add_argument('--disable-java')
            # 禁止弹出密码提示框
            if disable_password_alert:
                prefs = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
                options.add_experimental_option('prefs', prefs)
            # 禁用浏览器弹窗
            if disable_browser_alert:
                pref = {'profile.default_content_setting_values': {'notifications': 2}}
                options.add_experimental_option('prefs', pref)
            # 添加插件
            if crx_plugin_list:
                for crx_plugin in crx_plugin_list:
                    options.add_extension(crx_plugin)
        # 创建浏览器
        self.chrome = Chrome(executable_path=executable_path, options=options)
        self.wait = WebDriverWait(self.chrome, wait_time)

    def get_element(self, pattern, mode='xpath'):
        """
        通过xpath获取元素
        :param pattern: xpath表达式
        :param mode: 查找元素的方式
        :return:
        """
        mode_dict = {
            'xpath': By.XPATH,
            'id': By.ID,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT,
            'name': By.NAME,
            'tag_name': By.TAG_NAME,
            'class_name': By.CLASS_NAME,
            'css_selector': By.CSS_SELECTOR,
        }
        return self.wait.until(ec.presence_of_element_located((mode_dict[mode], pattern)))

    def get_element_text(self, pattern, mode='xpath'):
        """
        获取元素文本
        :param pattern: xpath表达式
        :param mode: 查找元素的方式
        :return:
        """
        return self.get_element(pattern, mode=mode).text

    def get_element_attribute(self, pattern, attribute, mode='xpath'):
        """
        通过xpath获取元素
        :param pattern: xpath表达式
        :param attribute: 属性名
        :param mode: 查找元素的方式
        :return:
        """
        return self.get_element(pattern, mode=mode).get_attribute(attribute)

    def get_element_property(self, pattern, _property, mode='xpath'):
        """
        通过xpath获取元素
        :param pattern: xpath表达式
        :param _property: 性质名
        :param mode: 查找元素的方式
        :return:
        """
        return self.get_element(pattern, mode=mode).get_property(_property)

    def get_elements(self, pattern, mode='xpath'):
        """
        通过xpath获取元素
        :param pattern: xpath表达式
        :param mode: 查找元素的方式
        :return:
        """
        mode_dict = {
            'xpath': By.XPATH,
            'id': By.ID,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT,
            'name': By.NAME,
            'tag_name': By.TAG_NAME,
            'class_name': By.CLASS_NAME,
            'css_selector': By.CSS_SELECTOR,
        }
        return self.wait.until(ec.presence_of_all_elements_located((mode_dict[mode], pattern)))

    def get_elements_text(self, pattern, mode='xpath'):
        """
        获取元素文本
        :param pattern: xpath表达式
        :param mode: 查找元素的方式
        :return:
        """
        return [x.text for x in self.get_elements(pattern, mode=mode)]

    def get_elements_attribute(self, pattern, attribute, mode='xpath'):
        """
        通过xpath获取元素
        :param pattern: xpath表达式
        :param attribute: 属性名
        :param mode: 查找元素的方式
        :return:
        """
        return [x.get_attribute(attribute) for x in self.get_elements(pattern, mode=mode)]

    def get_elements_property(self, pattern, _property, mode='xpath'):
        """
        通过xpath获取元素
        :param pattern: xpath表达式
        :param _property: 性质名
        :param mode: 查找元素的方式
        :return:
        """
        return [x.get_property(_property) for x in self.get_elements(pattern, mode=mode)]

    def click_element(self, pattern, mode='xpath'):
        """
        点击元素对象
        :param pattern: xpath表达式
        :param mode: 查找元素的方式
        :return:
        """
        self.get_element(pattern, mode=mode).click()

    def send_keys_to_element(self, value, pattern, clear=True, mode='xpath'):
        """
        给元素对象中输入文本
        :param value: 要输入的文本
        :param pattern: xpath表达式
        :param clear:  是否清空文本
        :param mode: 查找元素的方式
        :return:
        """
        ele = self.get_element(pattern, mode=mode)
        # 清空文本
        if clear:
            ele.clear()
        ele.send_keys(value)

    def click_element_by_js(self, element):
        """
        通过js方式点击元素
        :param element: 元素对象
        :return:
        """
        self.chrome.execute_script('arguments[0].click();', element)

    def scroll_to_element_by_js(self, element):
        """
        通过js方式滑动到指定元素的位置
        :param element: 元素对象
        :return:
        """
        self.chrome.execute_script('arguments[0].scrollIntoView();', element)

    def scroll_to(self, height=10000):
        """
        滚动到指定位置
        :param height: 指定高度
        :return:
        """
        self.chrome.execute_script('document.documentElement.scrollTop={}'.format(height))

    def scroll(self, move=10000):
        """
        向下滚动到指定距离
        :param move: 指定高度
        :return:
        """
        self.chrome.execute_script('')

    def scroll_to_top(self):
        """
        滚动到指定位置
        :return:
        """
        self.scroll_to(height=0)

    def scroll_to_body_bottom(self):
        """
        滚动到底部
        :return:
        """
        self.chrome.execute_script('window.scrollTo(0, document.body.scrollHeight)')

    def __del__(self):
        """
        若浏览器未退出，则退出浏览器
        浏览器退出时，若有插件，则删除插件
        :return:
        """
        try:
            self.chrome.quit()
            if self.proxy_plugin_path:
                os.remove(self.proxy_plugin_path)
        except:
            pass


def run():
    pass


if __name__ == '__main__':
    pass
