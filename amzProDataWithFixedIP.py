# -*- codeing = utf-8 -*-
# @Time : 2020/10/1 19:39
# @Author : Cj
# @File : amzAction.py
# @Software : PyCharm

import os
import random
import re
import traceback
from datetime import datetime
from time import sleep

from fake_useragent import UserAgent
from pymysql import IntegrityError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from db import MysqlPool
from logger import Logger

all_log = Logger('log/amz-pro-fixed-ip-all.log', level='debug')
error_log = Logger('log/amz-pro-fixed-ip-error.log', level='error')
desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def getProData():
    mp = MysqlPool()
    data_sql = "select * from amz123_keyword_left9 where status is null or status=0 order by id limit 2000"
    data_list = mp.fetch_all(data_sql,None)
    for data in data_list:
        os.system("taskkill /f /im chrome.exe /t")
        proxy = "C:\\py_file\\proxyauth\\%s"%os.listdir("C:\\py_file\\proxyauth")[random.randint(0,4)]
        # proxy = 1
        all_log.logger.info("---ip=%s,keyword=%s开始采集---"%(proxy,data['keyword']))
        ua = UserAgent().chrome
        options = webdriver.ChromeOptions()
        options.add_extension(proxy)
        options.add_argument("user-agent=" + ua)
        # options.add_argument("--start-maximized")
        # options.add_argument("--headless")
        options.add_argument('blink-settings=imagesEnabled=false')
        options.add_argument("--disable-gpu")
        options.add_argument("log-level=3")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(600,600)
        cookies = [{'domain': 'www.amazon.com', 'expiry': 1632329890, 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': False, 'value': 'tb:s-TW8A7SAQXE5512HEHN3F|1602089889292&t:1602089890223&adb:adblk_no'}, {'domain': '.amazon.com', 'expiry': 2082787202, 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': False, 'value': 'en_US'}, {'domain': '.amazon.com', 'expiry': 1633625853, 'httpOnly': False, 'name': 'session-token', 'path': '/', 'secure': True, 'value': '3QBwaC0p4MPUmPmkTggA/5KFuQV86y0YLrdo7ONa0Jj32bh7dV8URjqYgcRBuBz3ADk9Svq0h89qS1OuCpZy+uA1IYfO1TNpiYJaP6z6zHy2O/AO4FlwdTphm7+S2ahm1LBYNUTY+xDrwGQmgF8u6Dqx7nXqXJNSOkBCdVrQZ6a30LnhBpQgwinDvWxMFeKNsbK8LnDO+tARUPQiRm0va3zvb4gqiUAPSBe8RxIeunmQvASbwAR4Yc1WHotY6utU'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'ubid-main', 'path': '/', 'secure': True, 'value': '134-4542133-6572654'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id-time', 'path': '/', 'secure': False, 'value': '2082787201l'}, {'domain': '.amazon.com', 'expiry': 1633625846, 'httpOnly': False, 'name': 'i18n-prefs', 'path': '/', 'secure': False, 'value': 'USD'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id', 'path': '/', 'secure': True, 'value': '132-8928912-9834042'}]
        driver.get("https://www.baidu.com")
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'su')))
        except:
            error_log.logger.error("---%s打开百度失败---"%proxy)
            continue
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        sleep(0.5)
        driver.get("https://www.amazon.com/s?k=" + data['keyword'] + "&ref=nb_sb_noss")
        try:
            WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//div[contains(@class,"s-main-slot")]')))
        except:
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//h4[contains(text(),"characters you see")]')))
                error_log.logger.error(
                    "***ip=%s,keyword=%s,出现验证码,结束当前采集***" % (proxy, data['keyword']))
                driver.quit()
                continue
            except:
                pass
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//div[contains(@class,"s-main-slot")]')))
            except:
                error_log.logger.error(
                    "***ip=%s,keyword=%s,页面采集错误,结束当前采集***" % (proxy, data['keyword']))
                driver.quit()
                continue
        divs = driver.find_elements_by_xpath('//div[contains(@class,"s-main-slot")]/div')
        try:
            success_num = 0
            update_sql = "update amz123_keyword_left9 set status=1 where id=%s"
            for div in divs:
                asin = div.get_attribute('data-asin')
                if asin and str(asin).startswith("B"):
                    try:
                        div.find_element_by_xpath('.//div[@class="a-row a-spacing-micro"]')
                        sponsored = "1"
                    except:
                        pass
                        sponsored = "0"
                    try:
                        price = div.find_element_by_xpath('.//span[@data-a-color="base"]/span').get_attribute("innerText").replace(
                            "$", "")
                    except:
                        price = None
                    try:
                        img1 = div.find_element_by_xpath('.//img').get_attribute('src')
                    except:
                        img1 = None
                    try:
                        title = div.find_element_by_xpath('.//h2/a/span').get_attribute("innerText")
                    except:
                        title = None
                    try:
                        div.find_element_by_xpath('.//span[contains(text(),"by Amazon")]')
                        fba = "1"
                    except:
                        fba = "0"
                    try:
                        star = div.find_element_by_xpath('.//div[@class="a-row a-size-small"]/span').get_attribute('aria-label').replace(" out of 5 stars","")
                    except:
                        star = None
                    try:
                        review = div.find_element_by_xpath('.//div[@class="a-row a-size-small"]/span[2]').get_attribute(
                            'aria-label').replace(",", "")
                    except:
                        review = "0"
                    try:
                        if int(review) > 70:
                            all_log.logger.info("---%s评价数为%s,跳过---"%(asin,review))
                            continue
                        if float(price) > 40:
                            all_log.logger.info("---%s价格为%s,跳过---" % (asin, price))
                            continue
                        if sponsored == "1":
                            all_log.logger.info("---%s为广告,跳过---" % asin)
                            continue
                    except:
                        all_log.logger.info("---%s过滤报错,跳过---" % asin)
                        continue
                    pro_url = div.find_element_by_xpath('.//h2/a').get_attribute("href")
                    js = 'window.open("' + pro_url + '")'
                    driver.execute_script(js)
                    driver.switch_to.window(driver.window_handles[1])
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.visibility_of_element_located((By.ID, 'bylineInfo_feature_div')))
                        try:
                            brand = driver.find_element_by_xpath('//a[@id="bylineInfo"]').text.replace('Brand: ',
                                                                                                       '').replace(
                                'Visit the ', '').replace('Store', '').strip()
                        except:
                            brand = None
                        try:
                            store = filter_str(driver.find_element_by_id('sellerProfileTriggerId').text)
                        except:
                            store = None
                        try:
                            qa = driver.find_element_by_xpath('//*[@id="askATFLink"]/span').get_attribute(
                                'innerText').replace(" answered questions", "")
                        except:
                            qa = "0"
                        try:
                            seller_id = driver.find_element_by_id('merchantID').get_attribute("value")
                        except:
                            seller_id = None
                        try:
                            seller_num = driver.find_element_by_xpath(
                                '//div[@id="olp-upd-new-freeshipping-threshold"]//a/span').text
                            seller_num = re.findall("\((.*)\)", seller_num)[0]
                        except:
                            seller_num = 0
                        br_error_num = 0
                        rank_type = 0
                        big_rank_txt = ""
                        big_rank = 0
                        mid_rank_txt = ""
                        mid_rank = 0
                        small_rank_txt = ""
                        small_rank = 0
                        while big_rank_txt == "":
                            if rank_type == 1:
                                try:
                                    big_rank_txt = driver.find_element_by_xpath(
                                        '//div[@id="detailBullets_feature_div"]/following-sibling::ul').get_attribute(
                                        'innerText')
                                    if big_rank_txt == "":
                                        br_error_num += 1
                                except:
                                    br_error_num += 1
                                    sleep(1)
                                    big_rank_txt = ""
                            else:
                                try:
                                    big_rank_txt = getRank(driver, 1)
                                except:
                                    try:
                                        WebDriverWait(driver, 5).until(
                                            EC.visibility_of_element_located(
                                                (By.ID, 'detailBulletsWrapper_feature_div')))
                                        rank_type = 1
                                        big_rank_txt = driver.find_element_by_xpath(
                                            '//div[@id="detailBullets_feature_div"]/following-sibling::ul').get_attribute(
                                            'innerText')
                                    except:
                                        br_error_num += 1
                                        sleep(1)
                                        big_rank_txt = ""
                            if br_error_num == 3:
                                all_log.logger.error("%s未采集到大类排名%s次" % (asin, br_error_num))
                                big_rank_txt = ""
                                break
                        if big_rank_txt != "":
                            if rank_type == 0:
                                big_rank_txt = re.sub("\(.*", "", big_rank_txt).strip()
                                big_rank_list = re.findall("\d", big_rank_txt)
                                big_rank = ""
                                for br in big_rank_list:
                                    big_rank += br
                            else:
                                for br_i, br in enumerate(big_rank_txt.split("#")):
                                    rank_txt = "#" + br.strip()
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
                                mid_rank_txt = getRank(driver, 2)
                            except:
                                mid_rank_txt = ""
                            if mid_rank_txt != "":
                                mid_rank_txt = re.sub("\(.*", "", mid_rank_txt).strip()
                                mid_rank_list = re.findall("\d", mid_rank_txt)
                                mid_rank = ""
                                for mr in mid_rank_list:
                                    mid_rank += mr
                            else:
                                mid_rank = 0
                            try:
                                small_rank_txt = getRank(driver, 3)
                            except:
                                small_rank_txt = ""
                            if small_rank_txt != "":
                                small_rank_txt = re.sub("\(.*", "", small_rank_txt).strip()
                                small_rank_list = re.findall("\d", small_rank_txt)
                                small_rank = ""
                                for sr in small_rank_list:
                                    small_rank += sr
                            else:
                                small_rank = 0
                        try:
                            put_date = driver.find_element_by_xpath(
                                '//th[contains(text(),"Date First Available")]/following-sibling::td[1]').get_attribute(
                                'innerText')
                            if put_date:
                                put_date = datetime.strptime(put_date, '%B %d, %Y').strftime("%Y-%m-%d")
                        except:
                            put_date = None
                        if big_rank == '' or int(big_rank) == 0 or int(big_rank) > 15000:
                            all_log.logger.info("---%s大类排名为%s,跳过---" % (asin, big_rank))
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            continue
                        img2 = ''
                        img3 = ''
                        img2_num = 0
                        img2_click_num = 0
                        img3_num = 0
                        img3_click_num = 0
                        while img2 == '' and img2_click_num < 40 and img2_num < 5:
                            sleep(0.5)
                            try:
                                driver.find_element_by_xpath(
                                    '//div[@id="altImages"]/ul//li[@class="a-spacing-small template"]/following-sibling::li[2]').click()
                            except:
                                img2_click_num += 1
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.visibility_of_element_located((By.XPATH, '//li[contains(@class,"itemNo1")]')))
                                img2 = driver.find_element_by_xpath(
                                    '//li[contains(@class,"itemNo1")]//img').get_attribute("src")
                            except:
                                img2_num += 1
                        while img3 == '' and img3_click_num < 40 and img3_num < 5:
                            sleep(0.5)
                            try:
                                driver.find_element_by_xpath(
                                    '//div[@id="altImages"]/ul//li[@class="a-spacing-small template"]/following-sibling::li[3]').click()
                            except:
                                img3_click_num += 1
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.visibility_of_element_located((By.XPATH, '//li[contains(@class,"itemNo2")]')))
                                img3 = driver.find_element_by_xpath(
                                    '//li[contains(@class,"itemNo2")]//img').get_attribute("src")
                            except:
                                img3_num += 1
                        sql = "insert into tb_amz_pro_1129(keyword,asin,img1,img2,img3,sponsored,price,title,fba,star,review,brand,store,qa,seller_id,seller_num," \
                              "big_rank_txt,big_rank,mid_rank_txt,mid_rank,small_rank_txt,small_rank,put_date,add_date) " \
                              "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())"
                        sql_param = [data['keyword'], asin, img1,img2,img3, sponsored, price, title, fba, star, review, brand,store, qa,seller_id,
                                     seller_num,big_rank_txt, big_rank, mid_rank_txt, mid_rank, small_rank_txt, small_rank,put_date]
                        try:
                            mp.insert(sql, sql_param)
                            all_log.logger.info("-----%s(%s)入库成功-----" % (asin, data['keyword']))
                            success_num += 1
                        except IntegrityError:
                            all_log.logger.info("-----%s(%s)已存在-----" % (asin, data['keyword']))
                            success_num += 1
                        except Exception as e:
                            error_log.logger.error("-----%s(%s)入库失败%s-----" % (asin, data['keyword'],e))
                    except:
                        traceback.print_exc()
                        error_log.logger.error("-----%s---%s采集出错-----" % (data['keyword'], proxy))
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            mp.update(update_sql,(data['id'],))
        except:
            traceback.print_exc()
            error_log.logger.error("-----%s---%s出错-----" % (data['keyword'], proxy))
        finally:
            all_log.logger.info("---end---ip=%s,keyword=%s---" % (proxy, data['keyword']))
            driver.quit()

def bisector_list(tabulation: list, num: int):
    """
    将列表平均分成几份
    :param tabulation: 列表
    :param num: 份数
    :return: 返回一个新的列表
    """
    new_list = []

    '''列表长度大于等于份数'''
    if len(tabulation) >= num:
        '''remainder:列表长度除以份数，取余'''
        remainder = len(tabulation) % num
        if remainder == 0:
            '''merchant:列表长度除以分数'''
            merchant = int(len(tabulation) / num)
            '''将列表平均拆分'''
            for i in range(1, num + 1):
                if i == 1:
                    new_list.append(tabulation[:merchant])
                else:
                    new_list.append(tabulation[(i - 1) * merchant:i * merchant])
            return new_list
        else:
            '''merchant：列表长度除以分数 取商'''
            merchant = int(len(tabulation) // num)
            '''remainder:列表长度除以份数，取余'''
            remainder = int(len(tabulation) % num)
            '''将列表平均拆分'''
            for i in range(1, num + 1):
                if i == 1:
                    new_list.append(tabulation[:merchant])
                else:
                    new_list.append(tabulation[(i - 1) * merchant:i * merchant])
                    '''将剩余数据的添加前面列表中'''
                    if int(len(tabulation) - i * merchant) <= merchant:
                        for j in tabulation[-remainder:]:
                            new_list[tabulation[-remainder:].index(j)].append(j)
            return new_list
    else:
        '''如果列表长度小于份数'''
        for i in range(1, len(tabulation) + 1):
            tabulation_subset = [tabulation[i - 1]]
            new_list.append(tabulation_subset)
        return new_list

def removeTxtLine(txt,index):
    with open(txt) as fp_in:
        with open('temp.txt', 'w') as fp_out:
            fp_out.writelines(line for i, line in enumerate(fp_in) if i != index)
    os.rename(txt, 'test.bak')
    os.rename('temp.txt', txt)
    os.remove('test.bak')

def filter_str(desstr, restr=''):
    # 过滤除中英文及数字及英文标点以外的其他字符
    res = re.compile("[^\u4e00-\u9fa5^. !//_,$&%^*()<>+\"'?@#-|:~{}+|—^a-z^A-Z^0-9]")
    return res.sub(restr, desstr)

def getRank(driver,spanNum):
    rank_txt = driver.find_element_by_xpath(
        '//th[contains(text(),"Best Sellers Rank")]/following-sibling::td/span/span[%s]'%spanNum).get_attribute(
        'innerText')
    return rank_txt

if __name__ == "__main__":
    getProData()

