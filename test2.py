# -*- codeing = utf-8 -*-
# @Time : 2020/10/1 19:39
# @Author : Cj
# @File : amzAction.py
# @Software : PyCharm

from selenium import webdriver
from datetime import datetime
import traceback,re,urllib.request,json,os,pymysql
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from db import MysqlPool
from multiprocessing import Pool
from logger import Logger
from time import sleep
import os,random

desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def getProData():
    ua = UserAgent().chrome
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=" + ua)
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    # options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--disable-gpu")
    options.add_argument("log-level=3")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.baidu.com")
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'su')))
    cookies = [{'domain': 'www.amazon.com', 'expiry': 1632329890, 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': False, 'value': 'tb:s-TW8A7SAQXE5512HEHN3F|1602089889292&t:1602089890223&adb:adblk_no'}, {'domain': '.amazon.com', 'expiry': 2082787202, 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': False, 'value': 'en_US'}, {'domain': '.amazon.com', 'expiry': 1633625853, 'httpOnly': False, 'name': 'session-token', 'path': '/', 'secure': True, 'value': '3QBwaC0p4MPUmPmkTggA/5KFuQV86y0YLrdo7ONa0Jj32bh7dV8URjqYgcRBuBz3ADk9Svq0h89qS1OuCpZy+uA1IYfO1TNpiYJaP6z6zHy2O/AO4FlwdTphm7+S2ahm1LBYNUTY+xDrwGQmgF8u6Dqx7nXqXJNSOkBCdVrQZ6a30LnhBpQgwinDvWxMFeKNsbK8LnDO+tARUPQiRm0va3zvb4gqiUAPSBe8RxIeunmQvASbwAR4Yc1WHotY6utU'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'ubid-main', 'path': '/', 'secure': True, 'value': '134-4542133-6572654'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id-time', 'path': '/', 'secure': False, 'value': '2082787201l'}, {'domain': '.amazon.com', 'expiry': 1633625846, 'httpOnly': False, 'name': 'i18n-prefs', 'path': '/', 'secure': False, 'value': 'USD'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id', 'path': '/', 'secure': True, 'value': '132-8928912-9834042'}]
    for cookie in cookies:
        driver.add_cookie(cookie_dict=cookie)
    sleep(1)
    driver.get("https://www.amazon.com/dp/B01GGOLHOQ")
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'bylineInfo_feature_div')))
    except:
        pass
    print(111)
    img2 = ''
    img3 = ''
    img2_num = 0
    img3_num = 0
    while img2 == '' and img2_num < 5:
        sleep(0.5)
        try:
            driver.find_element_by_xpath(
                '//div[@id="altImages"]/ul//li[@class="a-spacing-small template"]/following-sibling::li[2]').click()
        except:
            pass
        try:
            img2_num += 1
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//li[contains(@class,"itemNo1")]')))
            img2 = driver.find_element_by_xpath(
                '//li[contains(@class,"itemNo1")]//img').get_attribute("src")
        except:
            pass
    while img3 == '' and img3_num < 5:
        sleep(0.5)
        try:
            driver.find_element_by_xpath(
                '//div[@id="altImages"]/ul//li[@class="a-spacing-small template"]/following-sibling::li[3]').click()
        except:
            pass
        try:
            img3_num += 1
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//li[contains(@class,"itemNo2")]')))
            img3 = driver.find_element_by_xpath(
                '//li[contains(@class,"itemNo2")]//img').get_attribute("src")
        except:
            pass
    # try:
    #     driver.find_element_by_xpath('//div[@id="altImages"]/ul//li[4]').click()
    #     WebDriverWait(driver, 15).until(
    #         EC.visibility_of_element_located((By.XPATH, '//li[contains(@class,"itemNo1")]')))
    #     img2 = driver.find_element_by_xpath('//li[contains(@class,"itemNo1")]//img').get_attribute("src")
    # except:
    #     try:
    #         driver.find_element_by_xpath('//div[@id="altImages"]/ul//li[2]').click()
    #         sleep(3)
    #         img2 = driver.find_element_by_xpath(
    #             '//li[contains(@class,"itemNo1")]//img').get_attribute("src")
    #     except:
    #         pass
    # try:
    #     driver.find_element_by_xpath('//div[@id="altImages"]/ul//li[5]').click()
    #     sleep(3)
    #     img3 = driver.find_element_by_xpath(
    #         '//li[contains(@class,"itemNo2")]//img').get_attribute("src")
    # except:
    #     try:
    #         driver.find_element_by_xpath('//div[@id="altImages"]/ul//li[6]').click()
    #         sleep(3)
    #         img3 = driver.find_element_by_xpath(
    #             '//li[contains(@class,"itemNo2")]//img').get_attribute("src")
    #     except:
    #         pass
    # try:
    #     img4 = driver.find_element_by_xpath(
    #         '//li[contains(@class,"itemNo1")]//img').get_attribute("src")
    # except:
    #     img4 = ''

    print("img2="+img2,img2_num)
    print("img3=" + img3,img3_num)
    # print("img4=",img4)
    sleep(1000)

def getRank(driver,spanNum):
    rank_txt = driver.find_element_by_xpath(
        '//th[contains(text(),"Best Sellers Rank")]/following-sibling::td/span/span[%s]'%spanNum).get_attribute(
        'innerText')
    return rank_txt

if __name__ == "__main__":
    getProData()
    # a = {"a":1,"a2":2}
    # b = {"b":1,"b2":2}
    # c = []
    # c.append(a)
    # c.append(b)
    # print(len(c))
    # print(c)
    # c.pop(0)
    # print(len(c))
    # print(c)

    # a = '60.00 - 130.00'
    # a = a[0:a.index("-")]
    # print(a.strip())
    # proxy = os.listdir("D:\\proxy")
    # print(proxy[0])
    # random.randint(0,2)



