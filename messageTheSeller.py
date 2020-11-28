# -*- codeing = utf-8 -*-
# @Time : 2020/10/21 0:43
# @Author : Cj
# @File : messageTheSeller.py
# @Software : PyCharm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from multiprocessing import Process
from db import MysqlPool
from logger import Logger
import re,random,urllib.request,json,traceback
from fake_useragent import UserAgent
import sellerIdCollect

all_log = Logger('log/message_seller_all.log', level='debug')
desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def sendMessage(seller_list:list, process_name):
    if process_name == 0: own_shop = "A1XTOMSTOXPAYA"
    elif process_name == 1: own_shop = "A3G27BQJYXZZ9"
    else: own_shop = "A2DAVTN86TOFBR"
    seller_list.append({"seller_id": own_shop})
    seller_list.append({"seller_id": own_shop})
    options = Options()
    ua = UserAgent().chrome
    ua = re.sub("Chrome/\d{2}", "Chrome/"+str(random.randint(49,85)) , ua)
    options.add_argument("user-agent=" + ua)
    url = "http://ip.ipjldl.com/index.php/api/entry?method=proxyServer.tiqu_api_url&packid=0&fa=0&dt=0&groupid=0&fetch_key=&qty=1&time=1&port=1&format=json&ss=5&css=&dt=0&pro=&city=&usertype=6"
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("log-level=3")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    error_id = ""
    code_num = 0
    driver = None
    while True:
        break_flag = False
        seller_id = ""
        if code_num == 5:
            all_log.logger.error("验证码出现%s次，结束本次线程"%code_num)
            break
        try:
            ip_data = urllib.request.urlopen(url).read()
            print(ip_data)
            json_list = list(json.loads(ip_data)['data'])
            ip = "%s:%s" % (json_list[0]['IP'], json_list[0]['Port'])
            options.add_argument(('--proxy-server=http://' + ip))
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.baidu.com")
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'su')))
            cookies = [{'domain': 'www.amazon.com', 'expiry': 1633546766, 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': False, 'value': 'tb:s-9Y3R49PF708YQN2JSTQD|1603306765739&t:1603306766486&adb:adblk_no'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 'ubid-acbus', 'path': '/', 'secure': True, 'value': '135-5461869-9698219'}, {'domain': '.amazon.com', 'httpOnly': True, 'name': 'sst-main', 'path': '/', 'secure': True, 'value': 'Sst1|PQGmODmmRVTr4wTLLX7mC_VMCe0J3P52_mD3AvlkxGjwTeD5t2uFDgSPioYSnBPz5FAKe4eEMCynHWDP9mbjfHWeq27W_XPxCj7PjidcMlr7TLPMy0pnr6s_mUeQvv8G8ODlmUTJetjg2a8lcjR-x5paCvCJByvRtwGT37gKFa-ayxKUJsZbAv09O-TDHtkNVYqU3QxSvirmTT0eZCb2tzS63lFWSxGyP6BmOZP8NymMfpMUqe9XOMMgR02jZ_WwUy0ZYxmDo3MoC-Ygd_ernXnlFasORJS71q6HnPlois37w1Q'}, {'domain': '.amazon.com', 'httpOnly': True, 'name': 'sess-at-main', 'path': '/', 'secure': True, 'value': '"j58QvyLE4MrctxHR5TJl9z5ybqDxs1lLaviUqqlBo+c="'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 's_pers', 'path': '/', 'secure': True, 'value': '%20s_fid%3D0E27D31BD56383E9-3CFD0121F9F53866%7C1743088530834%3B%20s_dl%3D1%7C1585323930836%3B%20gpv_page%3DUS%253ASD%253ASOA-home%7C1585323930844%3B%20s_ev15%3D%255B%255B%2527www.baidu.com%2527%252C%25271584108648930%2527%255D%252C%255B%2527SCSOAStriplogin%2527%252C%25271584108685311%2527%255D%252C%255B%2527SCHelpUSSOA-header%2527%252C%25271585322130850%2527%255D%255D%7C1743088530850%3B'}, {'domain': '.amazon.com', 'expiry': 2082787200, 'httpOnly': False, 'name': 'session-token', 'path': '/', 'secure': False, 'value': '"bklqyXNcY2otHUrB0UC7lT3W06X4gp0jdezDNDRHh2erSpsdmsW+dIVeX1SgTkvpZCkF4m7Q7OzI9PGWB+oYC58Eqz6m1ALaqcwGi0tj0hZHeJpqolKUESA+rSmnK9zcN0ee+Ij4zSkL2QAmo52Xlc7r1wUWfxmNu0HGOkzWCVfHZXTCEPlamVQGgjS1sgW04UiCCHlJwXSwbrK/VAHJEqZs6htE4asMT0Xyh+xXLDuv7uBO8qEBvU93+RawA6NYI9pk13lAYn70Yzc3TcR/gA=="'}, {'domain': '.amazon.com', 'expiry': 1634842768, 'httpOnly': False, 'name': 'session-id', 'path': '/', 'secure': True, 'value': '130-2343992-9258319'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 'i18n-prefs', 'path': '/', 'secure': True, 'value': 'USD'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 's_nr', 'path': '/', 'secure': True, 'value': '1602604874325-Repeat'}, {'domain': '.www.amazon.com', 'httpOnly': False, 'name': 'csm-hit', 'path': '/', 'secure': True, 'value': 'tb:s-76JPR4REJEG0TFX5E92S|1603305423259&t:1603305423909&adb:adblk_no'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 's_vnum', 'path': '/', 'secure': True, 'value': '2016336910355%26vn%3D5'}, {'domain': '.amazon.com', 'expiry': 1634842768, 'httpOnly': False, 'name': 'session-id-time', 'path': '/', 'secure': False, 'value': '2082787201l'}, {'domain': '.www.amazon.com', 'httpOnly': False, 'name': 'csd-key', 'path': '/', 'secure': True, 'value': 'eyJ2IjoxLCJraWQiOiI4ZmNjYzIiLCJrZXkiOiJOclh4Vk9NNlFJNWhYNUU0Vk5LQUlDM0wzUjdUNkNHRjRmRDRqN3AwYkwwOWdvU1lvTWFEeWVmZEx6cVUreDVZZTJHWkVMVjBPZHFtLzlSWXlBanlBYmVsTXR2cmdUMkFLemswazdseU1xMWtjeG1YbFViWER6UHkzM1FZUHYzaHhKWmtDQWMvemVPS0VEdUNYdWhWNEZDM1pSemZ3UGdta0h4d2l1SW11Q05DL3lnNk03RC9hekFOVlhNblNVbVd0ZExjUktFNHRTQjczcnZseFRrUlRFVVVNMGp5cjN6M1NydzZGcjJTV0luYmREaVg0K0ppVzhGcGhUOWJldFlmWWNUMEp3T0V5UWRyc01CamxiRFhUVFFkNlRWU05GRkJDb2FHaTBBSVlqcGZUQW9FU0dOMlk4cGI2ZHJPQmswcUpEK2FUcWpLaS80amo1QWhJTXl3WEE9PSJ9'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 's_dslv', 'path': '/', 'secure': True, 'value': '1602604874334'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 'skin', 'path': '/', 'secure': False, 'value': 'noskin'}, {'domain': '.amazon.com', 'httpOnly': True, 'name': 'at-main', 'path': '/', 'secure': True, 'value': 'Atza|IwEBIIByFl3fO_epDc_IgeQmFoX01aOVdjk5pO0DjqFO588DFCgjQUrnfrFY4nj1xZrVhpwshh2PCPTvDb0YXgVqZueKhJHdQ4UJiblJE1x4VR2RmOsuSbq7jbLy5dh_-YvwZhX31TP65hf7XLzAU6cmwp-x-zBIynm4Wne7rzu6G3EH4JYE37ZIvbKsJ24HTS-LIbzhkkuJUFl6JUfNF1pIYAwa'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 'x-main', 'path': '/', 'secure': True, 'value': '"VRbmyyTVH@lveo2DxwcmgrjIvVrm7qyzrE2RdThu0TZ2Nnt8f9uIO8qepf9pmrE4"'}, {'domain': '.amazon.com', 'httpOnly': False, 'name': 'lc-main', 'path': '/', 'secure': True, 'value': 'en_US'}, {'domain': '.amazon.com', 'expiry': 1634842768, 'httpOnly': False, 'name': 'ubid-main', 'path': '/', 'secure': True, 'value': '132-8813534-9194430'}]
            for cookie in cookies:
                # try:cookie.pop('sameSite')
                # except:pass
                driver.add_cookie(cookie_dict=cookie)
            while len(seller_list) > 1:
                print("---第%s个线程剩余待发卖家数量%s---" % (process_name + 1, len(seller_list)))
                sleep(1)
                seller_id = seller_list[0]['seller_id']
                seller_url = "https://www.amazon.com/askseller?marketplaceID=ATVPDKIKX0DER&sellerID=%s&_encoding=UTF8&ref_=v_sp_contact_seller&"%seller_id
                driver.get(seller_url)
                sleep(2)
                try:
                    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//ul[@class="smartcs-buttons"]')))
                except:
                    try:
                        WebDriverWait(driver, 5).until(EC.title_contains('Amazon Sign-In'))
                        all_log.logger.error("%s页面cookies失效，第%s线程结束" %(seller_id,process_name+1))
                        return
                    except:
                        pass
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.XPATH, '//h4[contains(text(),"characters you see")]')))
                        code_num += 1
                        all_log.logger.error("%s页面出现验证码,结束当前采集" % seller_id)
                        break_flag = True
                        break
                    except:
                        pass
                    try:
                        WebDriverWait(driver, 5).until(EC.title_contains('Page Not Found'))
                        all_log.logger.error("%s页面未找到" %seller_id)
                        seller_list.pop(0)
                        continue
                    except:
                        pass
                driver.find_element_by_xpath('//li[@role="presentation"][2]').click()
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'smartcs-message-user')))
                driver.find_element_by_xpath('//ul[@class="smartcs-buttons"]/li[1]').click()
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, 'textarea')))
                driver.find_element_by_xpath('//textarea').send_keys("Does this product have 3 inche")
                sleep(1)
                driver.find_element_by_xpath('//span[text()="Send Message"]').click()
                seller_list.pop(0)
        except:
            traceback.print_exc()
            all_log.logger.error("***第%s个线程%s报错***" % (process_name + 1, seller_id))
            if error_id != "" and error_id == seller_id:
                seller_list.pop(0)
            else:
                error_id = seller_id
            if driver:
                driver.quit()
            continue
        if not break_flag:break
    all_log.logger.info("---第%s个线程运行结束---" % (process_name + 1))

if __name__ == "__main__":
    # mp = MysqlPool()
    # pool_num = 3
    # sql = "select seller_id from tb_seller_id limit 3,600"
    # all_seller_list = mp.fetch_all(sql, None)
    ll = [{"seller_id": "A26QSNPH3BN83U"},{"seller_id": "A1XTOMSTOXPAYA"},{"seller_id": "A3G27BQJYXZZ9"},{"seller_id": "A2DAVTN86TOFBR"}]
    sendMessage(ll,0)
    # lists = sellerIdCollect.bisector_list(all_seller_list, pool_num)
    # process_list = []
    # for p_num, p_list in enumerate(lists):
    #     sleep(0.5)
    #     process = Process(target=sendMessage, args=(p_list, p_num,))
    #     process.start()
    #     process_list.append(process)
    # for p in process_list:
    #     p.join()
    all_log.logger.info("***所有线程运行结束***")
