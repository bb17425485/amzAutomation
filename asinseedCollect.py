# -*- codeing = utf-8 -*-
# @Time : 2020/10/1 19:39
# @Author : Cj
# @File : amzAction.py
# @Software : PyCharm

from selenium import webdriver
import string,zipfile,os
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent
from logger import Logger
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from db import MysqlPool

all_log = Logger('log/asinseed_all.log', level='debug')
desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def collectData():



    ua = UserAgent().chrome
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=" + ua)
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_argument("--disable-gpu")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.baidu.com")
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'su')))
    except:
        all_log.logger.error("---打开百度失败---")
    cookies = [{'domain': 'www.asinseed.com', 'httpOnly': True, 'name': 'JSESSIONID', 'path': '/', 'secure': False, 'value': 'B0141BDB986A2D91ADCE21BCD1ACA3D2'}, {'domain': 'www.asinseed.com', 'expiry': 1609251926, 'httpOnly': False, 'name': 'asinseed-login-user', 'path': '/', 'secure': False, 'value': '4291529061IrZXNTSoIlHhPKyHGfg/7TMbw6xY7YpCjminsqgfQO1ekWtRZ9/kAs/qVnCI5AMe'}, {'domain': '.asinseed.com', 'expiry': 1638195927, 'httpOnly': False, 'name': 'ecookie', 'path': '/', 'secure': False, 'value': 'dWcWHqqTU5LL9saj_CN'}, {'domain': 'www.asinseed.com', 'expiry': 1606660198, 'httpOnly': False, 'name': 'crisp-client%2Fsocket%2Fb43aa37b-4c35-4551-a9d4-ad983960d40c', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '0'}, {'domain': '.asinseed.com', 'expiry': 1669731927, 'httpOnly': False, 'name': '_ga', 'path': '/', 'secure': False, 'value': 'GA1.2.1615561945.1606659387'}, {'domain': '.asinseed.com', 'expiry': 1622427931, 'httpOnly': False, 'name': 'crisp-client%2Fsession%2Fb43aa37b-4c35-4551-a9d4-ad983960d40c', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'session_f9e04788-6bf4-48fa-8a09-883989976e41'}, {'domain': '.asinseed.com', 'expiry': 1606659960, 'httpOnly': False, 'name': '_gat_gtag_UA_125163434_1', 'path': '/', 'secure': False, 'value': '1'}, {'domain': '.asinseed.com', 'expiry': 1606746327, 'httpOnly': False, 'name': '_gid', 'path': '/', 'secure': False, 'value': 'GA1.2.1043797262.1606659387'}, {'domain': '.asinseed.com', 'expiry': 1922019384, 'httpOnly': False, 'name': 'w_guest', 'path': '/', 'secure': False, 'value': 'NpicHiupaa1M_201129-223501'}]
    for cookie in cookies:
        driver.add_cookie(cookie_dict=cookie)
    sleep(0.5)
    mp = MysqlPool()
    trend_sql = "select t.* from selected_products t where t.trend_data is null or t.trend_data=''"
    trend_data_list = mp.fetch_all(trend_sql, None)
    for trend_data in trend_data_list:
        driver.get("https://www.asinseed.com/en/US?q=%s"%trend_data['keyword'])
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="morris-table-inline"]')))
        trs = driver.find_elements_by_xpath('//div[@class="morris-table-inline"]/../..')
        searches = ''
        for tr in trs:
            if trend_data['keyword'] == tr.find_element_by_xpath('./td[2]').text:
                searches = eval(tr.find_element_by_xpath('./td[3]/div').get_attribute("data-y"))
        if searches == '':
            searches = eval(driver.find_element_by_xpath('//div[@class="morris-table-inline"]').get_attribute("data-y"))
        update_sql = "update selected_products set trend_data=%s where id=%s"
        update_param = [str(searches),trend_data['id']]
        mp.insert(update_sql,update_param)
        all_log.logger.info("---%s趋势采集成功---"%trend_data['asin'])
        sleep(1)

    asin_sql = "select t.* from selected_products t where t.id not in (select t2.main_id from asin_searches t2 where t2.main_id=t.id)"
    asin_data_list = mp.fetch_all(asin_sql,None)
    for asin_data in asin_data_list:
        driver.get("https://www.asinseed.com/en/US?q=%s" % asin_data['asin'])
        WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//td[@class="text-right"]')))
        trs = driver.find_elements_by_xpath('//td[@class="text-right"]/..')
        insert_sql = "insert into asin_searches(main_id,asin,keyword,searches,add_time) values"
        update_param = []
        for tr in trs:
            keyword = tr.find_element_by_xpath('./td').text
            searches = tr.find_element_by_xpath('./td[2]').text.replace(",","")
            if searches is None or searches == "":
                searches = 0
            insert_sql += "(%s,%s,%s,%s,now()),"
            update_param.append(asin_data['id'])
            update_param.append(asin_data['asin'])
            update_param.append(keyword)
            update_param.append(searches)
        if insert_sql.endswith(","):
            insert_sql = insert_sql[:-1]
        mp.insert(insert_sql,update_param)
        all_log.logger.info("---%s关联关键词成功---" % asin_data['asin'])
        sleep(1)


if __name__ == "__main__":
    collectData()
