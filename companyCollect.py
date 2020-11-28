# -*- codeing = utf-8 -*-
# @Time : 2020/10/29 17:30
# @Author : Cj
# @File : companyCollect.py
# @Software : PyCharm

from selenium import webdriver
import traceback,re,urllib.request,json,os,pymysql,random
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from apscheduler.schedulers.blocking import BlockingScheduler
from db import MysqlPool
from multiprocessing import Pool,Process
from logger import Logger
from time import sleep

all_log = Logger('log/company_collect_all.log', level='debug')
desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def getBusinessName(seller_list, process_name):
    ua = UserAgent(verify_ssl=False).chrome
    ua = re.sub("Chrome/\d{2}", "Chrome/" + str(random.randint(49, 85)), ua)
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=" + ua)
    url = "http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.tiqu_api_url&packid=0&fa=0&dt=0&groupid=0&fetch_key=&qty=1&time=1&port=1&format=json&ss=5&css=&dt=0&pro=&city=&usertype=6"
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    driver = None
    error_url = ""
    while True:
        asin_url = ""
        try:
            ip_data = urllib.request.urlopen(url).read()
            print(ip_data)
            json_list = list(json.loads(ip_data)['data'])
            ip = "%s:%s" % (json_list[0]['IP'], json_list[0]['Port'])
            options.add_argument(('--proxy-server=http://' + ip))
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.baidu.com")
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'su')))
            cookies = [{'domain': 'www.amazon.com', 'expiry': 1633407103, 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': False, 'value': 'tb:s-Z135Q1Y24PZMTTNF8DDZ|1603167100870&t:1603167103192&adb:adblk_no'}, {'domain': '.amazon.com', 'expiry': 2082787201, 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': False, 'value': 'en_US'}, {'domain': '.amazon.com', 'expiry': 1634703091, 'httpOnly': False, 'name': 'session-token', 'path': '/', 'secure': True, 'value': 'fxzmNhMySgaV1gVga7nbDig972AmQGFxhFgyEZISkgU6//KEtZqCk54TxZV/ttWlmA+5gxnaUgZzFBKseUNhVdQgTHbVI7sDvNIFguqFFGDHATp9swCwfYcd3ViRzafe3d9YkzdIfga0G4kRm5SyB8MRExx3AnOc6jNxeMYPpYxuhaZX8Pe3viZFX6OK551eUxMz5vMEzje8b4ugkSCVV5OKFaJsgqL/iFHyHqnntlRSPPiPwK1eZ2gUicC09p3Q'}, {'domain': '.amazon.com', 'expiry': 1634703109, 'httpOnly': False, 'name': 'session-id-time', 'path': '/', 'secure': False, 'value': '2082787201l'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 'skin', 'path': '/', 'secure': False, 'value': 'noskin'}, {'domain': '.amazon.com', 'expiry': 1634703109, 'httpOnly': False, 'name': 'ubid-main', 'path': '/', 'secure': True, 'value': '130-0463586-1564060'}, {'domain': '.amazon.com', 'expiry': 1634703086, 'httpOnly': False, 'name': 'i18n-prefs', 'path': '/', 'secure': False, 'value': 'USD'}, {'domain': '.amazon.com', 'expiry': 1634703109, 'httpOnly': False, 'name': 'session-id', 'path': '/', 'secure': True, 'value': '147-0153722-0121323'}]
            for cookie in cookies:
                driver.add_cookie(cookie_dict=cookie)
            while len(seller_list) > 1:
                print("---第%s个线程剩余seller_id数量%s---" % (process_name+1,len(seller_list)))
                sleep(1)
                asin_url = "https://www.amazon.com/sp?seller="+str(seller_list[0]['seller_id'])
                driver.get(asin_url)
                try:
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, '//span[text()="Business Name:"]')))
                except:
                    WebDriverWait(driver, 5).until(EC.title_contains('Page Not Found'))
                    all_log.logger.error("%s页面未找到" % seller_list[0]['seller_id'])
                    seller_list.pop(0)
                    continue
                sleep(0.5)
                business_name = driver.find_element_by_xpath('//span[text()="Business Name:"]/..').text.replace("Business Name:","")
                if business_name:
                    update_sql = "update tb_seller_id set company=%s where seller_id=%s"
                    update_param = [business_name,seller_list[0]['seller_id']]
                    try:
                        update_mp = MysqlPool()
                        update_mp.update(update_sql,update_param)
                    except Exception as e:
                        all_log.logger.error("***%s入库报错%s***"%(seller_list[0]['seller_id'],e))
                seller_list.pop(0)
        except:
            all_log.logger.error("***第%s个线程%s报错***"%(process_name+1,asin_url))
            if error_url == asin_url:seller_list.pop(0)
            else:error_url = asin_url
            if driver:
                driver.quit()
            continue
        break
    all_log.logger.info("---第%s个线程运行结束---"%(process_name+1))


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

if __name__ == "__main__":
    # getBusinessName()

    mp = MysqlPool()
    pool_num = 3
    sql = "select seller_id from tb_seller_id order by id limit 600,9000"
    all_seller_list = mp.fetch_all(sql, None)
    # getBusinessName(all_seller_list,0)
    lists = bisector_list(all_seller_list, pool_num)
    process_list = []
    for p_num,p_list in enumerate(lists):
        sleep(0.5)
        process = Process(target=getBusinessName, args=(p_list,p_num,))
        process.start()
        process_list.append(process)
    for p in process_list:
        p.join()
    all_log.logger.info("运行结束")



