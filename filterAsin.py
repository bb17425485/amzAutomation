# -*- codeing = utf-8 -*-
# @Time : 2020/11/13 15:01
# @Author : Cj
# @File : filterAsin.py
# @Software : PyCharm

from selenium import webdriver
import traceback,re,urllib.request,json,os,pymysql,zipfile,string,configparser
from selenium.webdriver.support.wait import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from apscheduler.schedulers.blocking import BlockingScheduler
from db import MysqlPool
from datetime import datetime
from multiprocessing import Pool
from logger import Logger
from time import sleep

all_log = Logger('log/amz_filter.log', level='debug')
desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def findAsinByFilterTemp():
    sql = "SELECT asin,id from tb_filter_temp where status=1"
    total_list = mp.fetch_all(sql, None)
    url = "http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.tiqu_api_url&packid=0&fa=0&dt=0&groupid=0&fetch_key=&qty=1&time=2&port=1&format=json&ss=5&css=&dt=0&pro=&city=&usertype=6"
    driver = None
    update_sql = "update tb_filter_temp set status=1 where id=%s"
    while len(total_list) > 0:
        try:
            # ip_data = urllib.request.urlopen(url).read()
            # json_data = json.loads(ip_data)['data'][0]
            # ip = "%s:%s" % (json_data['IP'], json_data['Port'])
            # all_log.logger.info("---待分析asin数为%s,IP=%s---" % (len(total_list),ip))
            ua = UserAgent(verify_ssl=False).chrome
            options = webdriver.ChromeOptions()
            options.add_argument("user-agent=" + ua)
            # options.add_argument(('--proxy-server=http://' + ip))
            options.add_argument("--start-maximized")
            options.add_argument("--headless")
            options.add_argument('blink-settings=imagesEnabled=false')
            options.add_argument("--disable-gpu")
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            driver = webdriver.Chrome(options=options)
            config = configparser.RawConfigParser()
            config.read("config.ini", encoding="utf-8")
            cookies = config['account']['cookies']
            if type('') is type(cookies):cookies = eval(cookies)
            driver.get("https://www.baidu.com")
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'su')))
            for cookie in cookies:
                driver.add_cookie(cookie_dict=cookie)
            for db_obj in total_list:
                filter_list = []
                driver.get("https://www.amazon.com/dp/%s" % db_obj['asin'])
                try:
                    WebDriverWait(driver, 15).until(
                        EC.visibility_of_element_located((By.ID, 'rhf')))
                except:
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.ID, 'g')))
                        mp.update(update_sql,(db_obj['id'],))
                        all_log.logger.error("---%s页面变狗---" %db_obj['asin'] )
                        continue
                    except:
                        driver.close()
                        driver.quit()
                        break

                dp_asin_list_1 = driver.find_elements_by_xpath('//div[@id="dp"]//a[@class="a-size-small a-link-normal"]')
                for dp_asin in dp_asin_list_1:
                    review_num = dp_asin.get_attribute("innerText").replace(",","")
                    if review_num.isdecimal():
                        if int(review_num) <= 50:
                            filter_asin = filterAsinForStr(dp_asin.get_attribute("href"))
                            if filter_asin not in filter_list:
                                filter_list.append({"asin":filter_asin,"review":review_num})
                dp_asin_list_2 = driver.find_elements_by_xpath('//div[@id="dp"]//span[@class="a-color-link"]')
                for dp_asin_2 in dp_asin_list_2:
                    review_num = dp_asin_2.get_attribute("innerText").replace(",", "")
                    if review_num.isdecimal():
                        if int(review_num) <= 50:
                            filter_asin = dp_asin_2.find_element_by_xpath('./../../..').get_attribute("data-asin")
                            if filter_asin not in filter_list:
                                filter_list.append({"asin": filter_asin, "review": review_num})
                tr_asin_list = driver.find_elements_by_xpath('//tr[@id="comparison_custormer_rating_row"]//a[@class="a-link-normal"]')
                for tr_asin in tr_asin_list:
                    review_num = tr_asin.get_attribute("innerText").replace(",","").replace("(","").replace(")","")
                    if review_num.isdecimal():
                        if int(review_num) <= 50:
                            filter_asin = filterAsinForStr(tr_asin.get_attribute("href"))
                            if filter_asin not in filter_list:
                                filter_list.append({"asin":filter_asin,"review":review_num})
                all_log.logger.info("---%s页面符合筛选条件asin数为%s---" % (db_obj['asin'], len(filter_list)))
                if len(filter_list) > 2:
                    for db_asin in filter_list:
                        insert_sql = "insert into tb_filter_asin set main_id=%s,asin=%s,review=%s,add_time=now()"
                        insert_param = [db_obj['id'],db_asin['asin'],db_asin['review']]
                        mp.insert(insert_sql,insert_param)
                mp.update(update_sql,(db_obj['id'],))
                all_log.logger.info("---%s分析完成---" % db_obj['asin'])
        except Exception as e:
            traceback.print_exc()
            if driver is not None:
                driver.close()
                driver.quit()
        finally:total_list = mp.fetch_all(sql, None)
    all_log.logger.info("---asin过滤任务全部完成---")

def getDataByAsin():
    sql = "SELECT DISTINCT asin from tb_filter_asin where img = ''"
    total_list = mp.fetch_all(sql, None)
    driver = None
    url = "http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.tiqu_api_url&packid=0&fa=0&dt=0&groupid=0&fetch_key=&qty=1&time=2&port=1&format=json&ss=5&css=&dt=0&pro=&city=&usertype=6"
    while len(total_list) > 0:
        try:
            ip_data = urllib.request.urlopen(url).read()
            json_data = json.loads(ip_data)['data'][0]
            ip = "%s:%s" % (json_data['IP'], json_data['Port'])
            all_log.logger.info("---待采集asin数为%s,IP=%s---" % (len(total_list),ip))
            ua = UserAgent(verify_ssl=False).chrome
            options = webdriver.ChromeOptions()
            options.add_argument("user-agent=" + ua)
            options.add_argument(('--proxy-server=http://' + ip))
            options.add_argument("--start-maximized")
            options.add_argument("--headless")
            options.add_argument('blink-settings=imagesEnabled=false')
            options.add_argument("--disable-gpu")
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
            driver = webdriver.Chrome(options=options)
            config = configparser.RawConfigParser()
            config.read("config.ini", encoding="utf-8")
            cookies = config['account']['cookies']
            if type('') is type(cookies): cookies = eval(cookies)
            driver.get("https://www.baidu.com")
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'su')))
            for cookie in cookies:
                driver.add_cookie(cookie_dict=cookie)
            for db_obj in total_list:
                try:
                    driver.get("https://www.amazon.com/dp/%s" % db_obj['asin'])
                    # driver.get("https://www.amazon.com/dp/B07HC5GJ6Y")B086DQXZ33,B07HC5GJ6Y
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, 'bylineInfo_feature_div')))
                except:
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.ID, 'g')))
                        all_log.logger.error("---%s页面变狗---" % db_obj['asin'])
                        err_sql = "update tb_filter_asin set collect_type=1 where asin=%s"
                        mp.update(err_sql,(db_obj['asin'],))
                        total_list.remove(db_obj)
                        continue
                    except:
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.visibility_of_element_located((By.ID, 'gc-detail-page')))
                            all_log.logger.error("---%s--Gift Cards页面---" % db_obj['asin'])
                            err_sql = "update tb_filter_asin set collect_type=1 where asin=%s"
                            mp.update(err_sql, (db_obj['asin'],))
                            total_list.remove(db_obj)
                            continue
                        except:
                            all_log.logger.error("---%s页面异常---" % db_obj['asin'])
                            err_sql = "update tb_filter_asin set collect_type=2 where asin=%s"
                            mp.update(err_sql, (db_obj['asin'],))
                            total_list.remove(db_obj)
                            driver.close()
                            driver.quit()
                            break
                try:
                    title = driver.find_element_by_id('productTitle').get_attribute("innerText").strip()
                except:title = None
                try:
                    img = driver.find_element_by_xpath('//div[@id="altImages"]/ul//li[1]//img').get_attribute("src")
                    if img.endswith("png"):
                        img = driver.find_element_by_xpath('//div[@id="altImages"]/ul/li[4]//img').get_attribute("src")
                except:
                    try:
                        img = driver.find_element_by_xpath('//div[@id="altImages"]/ul/li[4]//img').get_attribute("src")
                    except:
                        try:
                            img = driver.find_element_by_xpath(
                                '//div[@id="altImages"]/ul/li[2]//img').get_attribute("src")
                        except: img = ''
                try:
                    fba = driver.find_element_by_xpath('//table[@id="tabular-buybox-container"]/tbody/tr/td[2]').text
                    if "Amazon" in str(fba):fba = 1
                    else:fba = 0
                except: fba = 0
                try:
                    price = driver.find_element_by_xpath('//span[@id="priceblock_saleprice"]').text.replace("$","").replace(",","")
                except:
                    try:
                        price = driver.find_element_by_xpath('//span[@id="priceblock_ourprice"]').text.replace("$", "").replace(",","")
                    except:price = None
                if price is not None and price.find("-") > -1:
                    price = price[0:price.index("-")].strip()
                try:
                    star = driver.find_element_by_xpath('//div[@id="centerCol"]//i[contains(@class,"a-icon a-icon-star")]/span').get_attribute("innerText").replace(" out of 5 stars","")
                except:star = None
                try:
                    seller_id = driver.find_element_by_id('merchantID').get_attribute("value")
                except:
                    seller_id = None
                try:
                    seller_num = driver.find_element_by_xpath('//div[@id="olp-upd-new-freeshipping-threshold"]//a/span').text
                    seller_num = re.findall("\((.*)\)",seller_num)[0]
                except:seller_num = 0
                try:
                    brand = driver.find_element_by_xpath('//a[@id="bylineInfo"]').text.replace('Brand: ', '').replace('Visit the ', '').replace('Store', '').strip()
                except:brand = None
                try:
                    store = filter_str(driver.find_element_by_id('sellerProfileTriggerId').text)
                except:store = None
                try:
                    qa = driver.find_element_by_xpath('//*[@id="askATFLink"]/span').get_attribute(
                        'innerText').replace(" answered questions", "")
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
                        all_log.logger.error("%s未采集到大类排名%s次" % (db_obj['asin'],br_error_num))
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
                # try:
                #     big_rank_txt = driver.find_element_by_xpath(
                #         '//table[@id="productDetails_detailBullets_sections1"]/tbody/tr[3]/td/span/span[1]').get_attribute(
                #         'innerText')
                # except:
                #     try:
                #         big_rank_txt = driver.find_element_by_xpath(
                #             '//*[@id="productDetails_detailBullets_sections1"]/tbody/tr[3]/td/span/span[1]').get_attribute(
                #             'innerText')
                #     except:
                #         big_rank_txt = ""
                # if big_rank_txt:
                #     big_rank_txt = re.sub("\(.*", "", big_rank_txt).strip()
                #     big_rank_list = re.findall("\d", big_rank_txt)
                #     big_rank = ""
                #     for br in big_rank_list:
                #         big_rank += br
                # else:
                #     big_rank = 0
                # try:
                #     mid_rank_txt = driver.find_element_by_xpath(
                #         '//table[@id="productDetails_detailBullets_sections1"]/tbody/tr[3]/td/span/span[2]').get_attribute(
                #         'innerText')
                # except:
                #     mid_rank_txt = ""
                # if mid_rank_txt:
                #     mid_rank_txt = re.sub("\(.*", "", mid_rank_txt).strip()
                #     mid_rank_list = re.findall("\d", mid_rank_txt)
                #     mid_rank = ""
                #     for mr in mid_rank_list:
                #         mid_rank += mr
                # else:
                #     mid_rank = 0
                # try:
                #     small_rank_txt = driver.find_element_by_xpath(
                #         '//table[@id="productDetails_detailBullets_sections1"]/tbody/tr[3]/td/span/span[3]').get_attribute(
                #         'innerText')
                # except:
                #     small_rank_txt = ""
                # if small_rank_txt:
                #     small_rank_txt = re.sub("\(.*", "", small_rank_txt).strip()
                #     small_rank_list = re.findall("\d", small_rank_txt)
                #     small_rank = ""
                #     for sr in small_rank_list:
                #         small_rank += sr
                # else:
                #     small_rank = 0
                try:
                    put_date = driver.find_element_by_xpath(
                        '//th[contains(text(),"Date First Available")]/following-sibling::td[1]').get_attribute(
                        'innerText')
                    if put_date:
                        put_date = datetime.strptime(put_date, '%B %d, %Y').strftime("%Y-%m-%d")
                except:
                    put_date = None
                # print("fba",fba,"seller_num",seller_num,"price",price,"img",img,"star",star,"seller_id",seller_id,"brand",brand,"store",store,"qa",qa,"big_rank",big_rank,"mid_rank",mid_rank,"small_rank",small_rank,"put_date",put_date)
                print(db_obj['asin'],"img", img)
                update_sql = "update tb_filter_asin set price=%s,title=%s,img=%s,store=%s,fba=%s,star=%s,brand=%s,seller_id=%s,qa=%s,seller_num=%s," \
                      "big_rank_txt=%s,big_rank=%s,mid_rank_txt=%s,mid_rank=%s,small_rank_txt=%s,small_rank=%s,put_date=%s,collect_type=1 where asin=%s"
                update_sql_param = [price, title, img, store,fba, star, brand,seller_id, qa,seller_num,big_rank_txt, big_rank,
                                    mid_rank_txt, mid_rank, small_rank_txt, small_rank,put_date,db_obj['asin']]
                mp.update(update_sql, update_sql_param)
                total_list.remove(db_obj)
                all_log.logger.info("---%s入库成功---"%db_obj['asin'])
        except TimeoutException:
            all_log.logger.error("---IP失效---")
            if driver is not None:
                driver.close()
                driver.quit()
        except Exception as e:
            traceback.print_exc()
            all_log.logger.error("---采集报错%s---"%e)
            total_list.pop(0)
            if driver is not None:
                driver.close()
                driver.quit()


def filterAsinForStr(asin_href):
    return re.findall("product-reviews/(.*)/ref",asin_href)[0]

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
    mp = MysqlPool()
    # findAsinByFilterTemp()
    getDataByAsin()
