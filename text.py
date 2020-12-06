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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

desired_capabilities = DesiredCapabilities.CHROME  # 修改页面加载策略
desired_capabilities["pageLoadStrategy"] = "none"  # 注释这两行会导致最后输出结果的延迟，即等待页面加载完成再输出

def test():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.baidu.com")
    cookies = [{'domain': 'www.asinseed.com', 'httpOnly': True, 'name': 'JSESSIONID', 'path': '/', 'secure': False, 'value': 'B0141BDB986A2D91ADCE21BCD1ACA3D2'}, {'domain': 'www.asinseed.com', 'expiry': 1609251926, 'httpOnly': False, 'name': 'asinseed-login-user', 'path': '/', 'secure': False, 'value': '4291529061IrZXNTSoIlHhPKyHGfg/7TMbw6xY7YpCjminsqgfQO1ekWtRZ9/kAs/qVnCI5AMe'}, {'domain': '.asinseed.com', 'expiry': 1638195927, 'httpOnly': False, 'name': 'ecookie', 'path': '/', 'secure': False, 'value': 'dWcWHqqTU5LL9saj_CN'}, {'domain': 'www.asinseed.com', 'expiry': 1606660198, 'httpOnly': False, 'name': 'crisp-client%2Fsocket%2Fb43aa37b-4c35-4551-a9d4-ad983960d40c', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '0'}, {'domain': '.asinseed.com', 'expiry': 1669731927, 'httpOnly': False, 'name': '_ga', 'path': '/', 'secure': False, 'value': 'GA1.2.1615561945.1606659387'}, {'domain': '.asinseed.com', 'expiry': 1622427931, 'httpOnly': False, 'name': 'crisp-client%2Fsession%2Fb43aa37b-4c35-4551-a9d4-ad983960d40c', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'session_f9e04788-6bf4-48fa-8a09-883989976e41'}, {'domain': '.asinseed.com', 'expiry': 1606659960, 'httpOnly': False, 'name': '_gat_gtag_UA_125163434_1', 'path': '/', 'secure': False, 'value': '1'}, {'domain': '.asinseed.com', 'expiry': 1606746327, 'httpOnly': False, 'name': '_gid', 'path': '/', 'secure': False, 'value': 'GA1.2.1043797262.1606659387'}, {'domain': '.asinseed.com', 'expiry': 1922019384, 'httpOnly': False, 'name': 'w_guest', 'path': '/', 'secure': False, 'value': 'NpicHiupaa1M_201129-223501'}]
    for cookie in cookies:
        driver.add_cookie(cookie_dict=cookie)
    sleep(0.5)
    driver.get("https://www.asinseed.com/en/US?q=wood%20gate")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="morris-table-inline"]')))
    data = driver.find_element_by_xpath('//div[@class="morris-table-inline"]').get_attribute("data-y")
    data_list = eval(data)
    print(data_list)
    sleep(1000)

if __name__ == "__main__":
    # test()
    a = '99999999,'
    print(a[:-1])
