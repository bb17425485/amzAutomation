# -*- codeing = utf-8 -*-
# @Time : 2020/10/1 19:39
# @Author : Cj
# @File : amzAction.py
# @Software : PyCharm
from typing import List, Any

from selenium import webdriver
import traceback,re,urllib.request,json,os,pymysql,zipfile,string
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from apscheduler.schedulers.blocking import BlockingScheduler
from db import MysqlPool
from multiprocessing import Pool
from logger import Logger
from time import sleep

all_log = Logger('log/amz-track-all.log', level='debug')
error_log = Logger('log/amz-track-error.log', level='error')
desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def getProData(ip,product_list):
    all_log.logger.info("***start***ip=%s,product_list=%s***"%(ip,len(product_list)))
    ua = UserAgent(verify_ssl=False).chrome
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=" + ua)
    if ip:
        options.add_argument(('--proxy-server=http://' + ip))
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
    driver = webdriver.Chrome(options=options)
    res_success_list = []
    try:
        driver.get("https://www.baidu.com")
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'su')))
        cookies = [{'domain': 'www.amazon.com', 'expiry': 1632329890, 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': False, 'value': 'tb:s-TW8A7SAQXE5512HEHN3F|1602089889292&t:1602089890223&adb:adblk_no'}, {'domain': '.amazon.com', 'expiry': 2082787202, 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': False, 'value': 'en_US'}, {'domain': '.amazon.com', 'expiry': 1633625853, 'httpOnly': False, 'name': 'session-token', 'path': '/', 'secure': True, 'value': '3QBwaC0p4MPUmPmkTggA/5KFuQV86y0YLrdo7ONa0Jj32bh7dV8URjqYgcRBuBz3ADk9Svq0h89qS1OuCpZy+uA1IYfO1TNpiYJaP6z6zHy2O/AO4FlwdTphm7+S2ahm1LBYNUTY+xDrwGQmgF8u6Dqx7nXqXJNSOkBCdVrQZ6a30LnhBpQgwinDvWxMFeKNsbK8LnDO+tARUPQiRm0va3zvb4gqiUAPSBe8RxIeunmQvASbwAR4Yc1WHotY6utU'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'ubid-main', 'path': '/', 'secure': True, 'value': '134-4542133-6572654'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id-time', 'path': '/', 'secure': False, 'value': '2082787201l'}, {'domain': '.amazon.com', 'expiry': 1633625846, 'httpOnly': False, 'name': 'i18n-prefs', 'path': '/', 'secure': False, 'value': 'USD'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id', 'path': '/', 'secure': True, 'value': '132-8928912-9834042'}]
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        sleep(1)
        for index,product in enumerate(product_list):
            all_log.logger.info("---开始跟踪%s(%s)---"%(product['keyword'],product['asin']))
            driver.get("https://www.amazon.com/s?k=" + product['keyword'] + "&ref=nb_sb_noss")
            pro_num = 0
            page_num = 1
            break_flag = False
            success_flag = True
            while True:
                try:
                    WebDriverWait(driver, 15).until(
                        EC.visibility_of_element_located((By.XPATH, '//ul[@class="a-pagination"]')))
                except:
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, '//h4[contains(text(),"characters you see")]')))
                        error_log.logger.error(
                            "***ip=%s,keyword=%s,asin=%s出现验证码,结束当前采集***" % (ip, product['keyword'], product['asin']))
                        driver.quit()
                        return res_success_list
                    except:
                        pass
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, '//ul[@class="a-pagination"]')))
                    except:
                        error_log.logger.error(
                            "***ip=%s,keyword=%s,asin=%s页面采集错误,结束当前采集***" % (ip, product['keyword'], product['asin']))
                        driver.quit()
                        return res_success_list
                divs = driver.find_elements_by_xpath('//div[contains(@class,"s-main-slot")]/div')
                for div in divs:
                    pro_asin = div.get_attribute('data-asin')
                    if pro_asin:
                        pro_num += 1
                        if pro_asin in str(product['asin']):
                            try:
                                #跳过广告
                                div.find_element_by_xpath('.//div[@class="a-row a-spacing-micro"]')
                                continue
                            except:
                                pass
                            try:
                                price = div.find_element_by_xpath('.//span[@data-a-color="base"]/span').get_attribute("innerText").replace(
                                    "$", "")
                            except:
                                price = None
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
                                div.find_element_by_xpath('.//span[contains(text(),"by Amazon")]')
                                fba = "1"
                            except:
                                fba = "0"
                            pro_url = div.find_element_by_xpath('.//h2/a').get_attribute("href")
                            js = 'window.open("' + pro_url + '")'
                            driver.execute_script(js)
                            driver.switch_to.window(driver.window_handles[1])
                            try:
                                WebDriverWait(driver, 15).until(
                                    EC.visibility_of_element_located((By.ID, 'bylineInfo_feature_div')))
                            except:
                                try:
                                    WebDriverWait(driver, 5).until(
                                        EC.visibility_of_element_located((By.XPATH, '//span[contains(text(),"未连接到互联网")]')))
                                    error_log.logger.error("网络连接断开")
                                    return res_success_list
                                except:
                                    error_log.logger.error("-----%s(%s)采集出错-----" % (product['keyword'], product['asin']))
                                    driver.close()
                                    driver.switch_to.window(driver.window_handles[0])
                                    break_flag = True
                                    success_flag = False
                                    break
                            try:
                                brand = driver.find_element_by_xpath('//a[@id="bylineInfo"]').text.replace('Brand: ', '')
                            except:
                                brand = None
                            try:
                                qa = driver.find_element_by_xpath('//*[@id="askATFLink"]/span').get_attribute(
                                    'innerText').replace(" answered questions", "").replace(",", "").replace("+", "")
                            except:
                                qa = "0"
                            seller = None
                            try:
                                follow_up_text = driver.find_element_by_xpath(
                                    '//div[@class="olp-text-box"]/span').get_attribute('innerText')
                                follow_up_list = re.findall("\d", follow_up_text)
                                for fu in follow_up_list:
                                    seller += fu
                            except:
                                pass
                            br_error_num = 0
                            rank_type = 0
                            big_rank_txt = ""
                            big_rank = 0
                            mid_rank_txt = ""
                            mid_rank = 0
                            small_rank_txt = ""
                            small_rank = 0
                            for_break_flag = False
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
                                if br_error_num == 5:
                                    print("未采集到大类排名%s次,退出" % br_error_num)
                                    for_break_flag = True
                                    break_flag = True
                                    success_flag = False
                                    break
                            if for_break_flag:
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
                            rank = pro_num
                            sql = "insert into tb_amz_track_data(pro_id,rank,page_num,price,fba,star,review,brand,qa,seller,big_rank_txt,big_rank,mid_rank_txt,mid_rank,small_rank_txt,small_rank,add_time) " \
                                  "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())"
                            sql_param = [product['id'], rank, page_num,price, fba, star, review, brand, qa, seller,big_rank_txt,
                                         big_rank, mid_rank_txt, mid_rank, small_rank_txt, small_rank]
                            try:
                                mp = MysqlPool()
                            except:
                                try:
                                    mp = MysqlPool()
                                except:
                                    error_log.logger.error("-----数据库连接失败-----")
                                    success_flag = False
                                    break_flag = True
                                    break
                            try:
                                mp.insert(sql, sql_param)
                                all_log.logger.info("***%s(%s)入库成功***" % (product['asin'], product['keyword']))
                                success_flag = False
                            except Exception:
                                error_log.logger.error("入库异常%s"%sql_param)
                                success_flag = False
                                break_flag = True
                                break
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            res_success_list.append(product)
                            break_flag = True
                            break
                if break_flag:
                    break
                if page_num == product['page_size']:
                    break
                try:
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, './/li[@class="a-last"]')))
                    driver.find_element_by_class_name('a-last').click()
                    page_num += 1
                except TimeoutException:
                    print("已到最后一页第%s页"%page_num)
                    break
            if success_flag:
                error_log.logger.error("---%s在%s的%s页内未找到---"%(product['asin'],product['keyword'],page_num))
                res_success_list.append(product)
    except Exception as e:
        traceback.print_exc()
        error_log.logger.error(e)
    finally:
        all_log.logger.info("---end---ip=%s,product_list=%s---" % (ip, product_list))
        driver.quit()
        return res_success_list

def getRank(driver,spanNum):
    rank_txt = driver.find_element_by_xpath(
        '//th[contains(text(),"Best Sellers Rank")]/following-sibling::td/span/span[%s]'%spanNum).get_attribute(
        'innerText')
    return rank_txt

def insetData(sql,param):
    mp = MysqlPool()
    mp.insertMany(sql, param)

def filter_str(desstr, restr=''):
    # 过滤除中英文及数字及英文标点以外的其他字符
    res = re.compile("[^\u4e00-\u9fa5^. !//_,$&%^*()<>+\"'?@#-|:~{}+|—^a-z^A-Z^0-9]")
    return res.sub(restr, desstr)

def removeTxtLine(txt,index):
    with open(txt) as fp_in:
        with open('temp.txt', 'w') as fp_out:
            fp_out.writelines(line for i, line in enumerate(fp_in) if i != index)
    os.rename(txt, 'test.bak')
    os.rename('temp.txt', txt)
    os.remove('test.bak')

def startTrack():
    url = "http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.tiqu_api_url&packid=0&fa=0" \
          "&dt=0&groupid=0&fetch_key=&qty=1&time=1&port=1&format=json&ss=5&css=&dt=0&pro=&city=&usertype=6"
    i = 1
    find_mp = MysqlPool()
    find_sql = "select * from tb_amz_track_pro where status=1"
    product_list = find_mp.fetch_all(find_sql, None)
    success_list = []
    track_list = [x for x in product_list if x not in success_list]
    all_log.logger.info("#######亚马逊关键词ASIN追踪开始#######")
    while len(track_list) > 0 and i < 10:
        ip_data = urllib.request.urlopen(url).read()
        json_list = list(json.loads(ip_data)['data'])
        json_data = json_list[0]
        ip = "%s:%s" % (json_data['IP'], json_data['Port'])
        success_list += getProData(ip, track_list)
        print("success_list=",len(success_list))
        track_list = [x for x in product_list if x not in success_list]
        all_log.logger.info("##########第%s轮追踪结束##########" % i)
        i += 1
    all_log.logger.info("#######亚马逊关键词ASIN追踪结束#######")

if __name__ == "__main__":
    # scheduler = BlockingScheduler()
    # scheduler.add_job(startTrack, 'cron', hour="0,3,6,9,12,15,18,21")
    # scheduler.start()
    startTrack()

