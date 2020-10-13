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

desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def getProData():
    ua = UserAgent().chrome
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=" + ua)
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("log-level=3")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.baidu.com")
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'su')))
    cookies = [{'domain': 'www.amazon.com', 'expiry': 1632329890, 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': False, 'value': 'tb:s-TW8A7SAQXE5512HEHN3F|1602089889292&t:1602089890223&adb:adblk_no'}, {'domain': '.amazon.com', 'expiry': 2082787202, 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': False, 'value': 'en_US'}, {'domain': '.amazon.com', 'expiry': 1633625853, 'httpOnly': False, 'name': 'session-token', 'path': '/', 'secure': True, 'value': '3QBwaC0p4MPUmPmkTggA/5KFuQV86y0YLrdo7ONa0Jj32bh7dV8URjqYgcRBuBz3ADk9Svq0h89qS1OuCpZy+uA1IYfO1TNpiYJaP6z6zHy2O/AO4FlwdTphm7+S2ahm1LBYNUTY+xDrwGQmgF8u6Dqx7nXqXJNSOkBCdVrQZ6a30LnhBpQgwinDvWxMFeKNsbK8LnDO+tARUPQiRm0va3zvb4gqiUAPSBe8RxIeunmQvASbwAR4Yc1WHotY6utU'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'ubid-main', 'path': '/', 'secure': True, 'value': '134-4542133-6572654'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id-time', 'path': '/', 'secure': False, 'value': '2082787201l'}, {'domain': '.amazon.com', 'expiry': 1633625846, 'httpOnly': False, 'name': 'i18n-prefs', 'path': '/', 'secure': False, 'value': 'USD'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id', 'path': '/', 'secure': True, 'value': '132-8928912-9834042'}]
    for cookie in cookies:
        driver.add_cookie(cookie_dict=cookie)
    sleep(1)
    driver.get("https://www.amazon.com/dp/B07D7WMM9H")
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'bylineInfo_feature_div')))
    except:
        pass
    try:
        brand = driver.find_element_by_xpath('//a[@id="bylineInfo"]').text.replace('Brand: ', '')
    except:
        brand = None
    try:
        qa = driver.find_element_by_xpath('//*[@id="askATFLink"]/span').get_attribute(
            'innerText').replace(" answered questions", "").replace(",", "").replace("+", "")
    except:
        qa = "0"
    br_error_num = 0
    rank_type = 0
    big_rank_txt = ""
    big_rank = 0
    mid_rank_txt = ""
    mid_rank = 0
    small_rank_txt = ""
    small_rank = 0
    while big_rank_txt != "":
        if rank_type == 1:
            try:
                big_rank_txt = driver.find_element_by_xpath(
                    '//div[@id="detailBullets_feature_div"]/following-sibling::ul').get_attribute(
                    'innerText')
            except:
                br_error_num += 1
                sleep(1)
                big_rank_txt = ""
        else:
            try:
                big_rank_txt = getRank(driver,1)
            except:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.ID, 'detailBulletsWrapper_feature_div')))
                    rank_type = 1
                    big_rank_txt = driver.find_element_by_xpath('//div[@id="detailBullets_feature_div"]/following-sibling::ul').get_attribute(
                        'innerText')
                except:
                    br_error_num += 1
                    sleep(1)
                    big_rank_txt = ""
        if br_error_num == 3:
            print("未采集到大类排名%s次,跳过" % br_error_num)
            break
    if big_rank_txt:
        if rank_type == 0:
            big_rank_txt = re.sub("\(.*", "", big_rank_txt).strip()
            big_rank_list = re.findall("\d", big_rank_txt)
            big_rank = ""
            for br in big_rank_list:
                big_rank += br
        else:
            for br_i,br in enumerate(big_rank_txt.split("#")):
                rank_txt = "#"+br.strip()
                if br_i == 1:
                    big_rank_txt = re.sub("\(.*", "", rank_txt).strip()
                    big_rank_list = re.findall("\d", big_rank_txt)
                    big_rank = ""
                    for br_1 in big_rank_list:
                        big_rank += br_1
                elif br_i == 2:
                    mid_rank_txt = rank_txt
                    mid_rank_list = re.findall("\d", mid_rank_txt)
                    mid_rank = ""
                    for mr in mid_rank_list:
                        mid_rank += mr
                elif br_i == 3:
                    small_rank_txt = rank_txt
                    small_rank_list = re.findall("\d", small_rank_txt)
                    small_rank = ""
                    for sr in small_rank_list:
                        small_rank += sr
    else:
        big_rank = 0
    if rank_type == 0:
        try:
            mid_rank_txt = getRank(driver,2)
        except:
            mid_rank_txt = ""
        if mid_rank_txt:
            mid_rank_txt = re.sub("\(.*", "", mid_rank_txt).strip()
            mid_rank_list = re.findall("\d", mid_rank_txt)
            mid_rank = ""
            for mr in mid_rank_list:
                mid_rank += mr
        else:
            mid_rank = 0
        try:
            small_rank_txt = getRank(driver,3)
        except:
            small_rank_txt = ""
        if small_rank_txt:
            small_rank_txt = re.sub("\(.*", "", small_rank_txt).strip()
            small_rank_list = re.findall("\d", small_rank_txt)
            small_rank = ""
            for sr in small_rank_list:
                small_rank += sr
        else:
            small_rank = 0
    try:
        put_date = driver.find_element_by_xpath(
            '//table[@id="productDetails_detailBullets_sections1"]/tbody/tr[4]/td').get_attribute(
            'innerText')
        if put_date:
            put_date = datetime.strptime(put_date, '%B %d, %Y').strftime("%Y-%m-%d")
    except:
        put_date = None
    print("big_rank_txt="+big_rank_txt)
    print("mid_rank_txt=" + mid_rank_txt)
    sleep(1000)

def getRank(driver,spanNum):
    rank_txt = driver.find_element_by_xpath(
        '//th[contains(text(),"Best Sellers Rank")]/following-sibling::td/span/span[%s]'%spanNum).get_attribute(
        'innerText')
    return rank_txt

if __name__ == "__main__":
    getProData()
