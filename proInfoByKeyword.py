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

all_log = Logger('log/amz-pro-all.log', level='debug')
error_log = Logger('log/amz-pro-error.log', level='error')
desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def getProData(ip,keyword):
    all_log.logger.info("***start***ip=%s,keyword=%s***"%(ip,keyword))
    ua = UserAgent().chrome
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=" + ua)
    if ip:
        options.add_argument(('--proxy-server=http://' + ip))
    # options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("log-level=3")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging','enable-automation'])
    driver = webdriver.Chrome(options=options)
    # driver.set_window_size(800,600)
    try:
        driver.get("https://www.baidu.com")
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'su')))
        cookies = [{'domain': 'www.amazon.com', 'expiry': 1632329890, 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': False, 'value': 'tb:s-TW8A7SAQXE5512HEHN3F|1602089889292&t:1602089890223&adb:adblk_no'}, {'domain': '.amazon.com', 'expiry': 2082787202, 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': False, 'value': 'en_US'}, {'domain': '.amazon.com', 'expiry': 1633625853, 'httpOnly': False, 'name': 'session-token', 'path': '/', 'secure': True, 'value': '3QBwaC0p4MPUmPmkTggA/5KFuQV86y0YLrdo7ONa0Jj32bh7dV8URjqYgcRBuBz3ADk9Svq0h89qS1OuCpZy+uA1IYfO1TNpiYJaP6z6zHy2O/AO4FlwdTphm7+S2ahm1LBYNUTY+xDrwGQmgF8u6Dqx7nXqXJNSOkBCdVrQZ6a30LnhBpQgwinDvWxMFeKNsbK8LnDO+tARUPQiRm0va3zvb4gqiUAPSBe8RxIeunmQvASbwAR4Yc1WHotY6utU'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'ubid-main', 'path': '/', 'secure': True, 'value': '134-4542133-6572654'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id-time', 'path': '/', 'secure': False, 'value': '2082787201l'}, {'domain': '.amazon.com', 'expiry': 1633625846, 'httpOnly': False, 'name': 'i18n-prefs', 'path': '/', 'secure': False, 'value': 'USD'}, {'domain': '.amazon.com', 'expiry': 1633625894, 'httpOnly': False, 'name': 'session-id', 'path': '/', 'secure': True, 'value': '132-8928912-9834042'}]
        for cookie in cookies:
            driver.add_cookie(cookie_dict=cookie)
        sleep(1)
        driver.get("https://www.amazon.com/s?k=" + keyword + "&ref=nb_sb_noss")
        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//div[contains(@class,"s-main-slot")]')))
        except:
            try:
                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.XPATH, '//h4[contains(text(),"characters you see")]')))
                error_log.logger.error(
                    "***ip=%s,keyword=%s,出现验证码,结束当前采集***" % (ip, keyword))
                driver.quit()
                return False,keyword
            except:
                pass
            try:
                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.XPATH, '//div[contains(@class,"s-main-slot")]')))
            except:
                error_log.logger.error(
                    "***ip=%s,keyword=%s,页面采集错误,结束当前采集***" % (ip, keyword))
                driver.quit()
                return False, keyword
        divs = driver.find_elements_by_xpath('//div[contains(@class,"s-main-slot")]/div')
        success_num = 0
        error_num = 0
        for div in divs:
            if error_num > 2:
                error_log.logger.error("-----%s采集出错超过%s次，退出采集-----" % (keyword,error_num))
                all_log.logger.info("-----已采集%s条ASIN-----" %success_num)
                if success_num > 20:
                    return True,keyword
                else:
                    return False, keyword
            try:
                asin = div.get_attribute('data-asin')
            except:
                sleep(1)
                error_num += 1
                continue
            if asin:
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
                    img = div.find_element_by_xpath('.//img').get_attribute('src')
                except:
                    img = None
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
                        all_log.logger.info("-----已采集%s条ASIN-----" % success_num)
                        if success_num > 20:
                            return True, keyword
                        else:
                            return False, keyword
                    except:
                        pass
                    error_log.logger.error("-----%s(%s)采集出错-----" % (keyword, asin))
                    error_num += 1
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
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
                            big_rank_txt = getRank(driver, 1)
                        except:
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.visibility_of_element_located((By.ID, 'detailBulletsWrapper_feature_div')))
                                rank_type = 1
                                big_rank_txt = driver.find_element_by_xpath(
                                    '//div[@id="detailBullets_feature_div"]/following-sibling::ul').get_attribute(
                                    'innerText')
                            except:
                                br_error_num += 1
                                sleep(1)
                                big_rank_txt = ""
                    if br_error_num == 3:
                        print("未采集到大类排名%s次,跳过" % br_error_num)
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
                    if mid_rank_txt  != "":
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
                    if small_rank_txt  != "":
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
                sql = "insert into tb_amz_pro(keyword,asin,img,sponsored,price,title,fba,star,review,brand,qa,big_rank_txt,big_rank,mid_rank_txt,mid_rank,small_rank_txt,small_rank,put_date,add_date) " \
                      "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())"
                sql_param = [keyword, asin, img, sponsored, price, title, fba, star, review, brand, qa,
                             big_rank_txt, big_rank, mid_rank_txt, mid_rank, small_rank_txt, small_rank,
                             put_date]
                try:
                    mp = MysqlPool()
                except:
                    try:
                        mp = MysqlPool()
                    except:
                        error_log.logger.error("-----数据库连接失败-----")
                        continue
                try:
                    mp.insert(sql, sql_param)
                    all_log.logger.info("***%s(%s)入库成功***" % (asin, keyword))
                except pymysql.err.IntegrityError:
                    print("重复入库")
                    pass
                except Exception:
                    error_log.logger.error("入库异常%s"%sql_param)
                    pass
                success_num += 1
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        return True,keyword
    except Exception as e:
        traceback.print_exc()
        error_log.logger.error(e)
        return False, keyword
    finally:
        all_log.logger.info("---end---ip=%s,keyword=%s---" % (ip, keyword))
        driver.quit()

def getRank(driver,spanNum):
    rank_txt = driver.find_element_by_xpath(
        '//th[contains(text(),"Best Sellers Rank")]/following-sibling::td/span/span[%s]'%spanNum).get_attribute(
        'innerText')
    return rank_txt

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

def insetData(sql,param):
    mp = MysqlPool()
    mp.insertMany(sql, param)

def removeTxtLine(txt,index):
    with open(txt) as fp_in:
        with open('temp.txt', 'w') as fp_out:
            fp_out.writelines(line for i, line in enumerate(fp_in) if i != index)
    os.rename(txt, 'test.bak')
    os.rename('temp.txt', txt)
    os.remove('test.bak')

if __name__ == "__main__":
    txt_name = "keyword_bak.txt"
    pool_num = 3
    keyword_list = []
    with open(txt_name, 'r') as f:
        for line in f.readlines():
            keyword_list.append(line.strip())
    num = len(keyword_list)
    url = "http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.tiqu_api_url&packid=0&fa=0" \
          "&dt=0&groupid=0&fetch_key=&qty=3&time=1&port=1&format=json&ss=5&css=&dt=0&pro=&city=&usertype=6"
    i = 1
    print('关键词总行数为%s行。' %num)
    all_log.logger.info("#######亚马逊关键词爬取开始#######")
    record = []
    while num > pool_num:
        ip_data = urllib.request.urlopen(url).read()
        json_list = list(json.loads(ip_data)['data'])
        param_list = []
        # for j in range(pool_num):
        for j,json_data in enumerate(json_list):
            # json_data = json_list[j]
            param = []
            ip = "%s:%s"%(json_data['IP'],json_data['Port'])
            param.append(ip)
            param.append(keyword_list[j])
            param_list.append(param)
        try:
            pool = Pool(len(json_list))
            # pool = Pool(pool_num)
            res_list = pool.starmap(getProData, param_list)
            pool.close()
            pool.join()
        except:
            continue
        for index,res in enumerate(res_list):
            removeTxtLine(txt_name, index)
            if not res[0]:
                with open("keyword_bak.txt", "a") as file:
                    file.write(res[1]+"\n")
        keyword_list = []
        with open(txt_name, 'r') as f:
            for line in f.readlines():
                keyword_list.append(line.strip())
        num = len(keyword_list)
        all_log.logger.info("##########第%s轮运行结束##########"%i)
        i += 1
    # getProData(None,"child proof door knob covers")

