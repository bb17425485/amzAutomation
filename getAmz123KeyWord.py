# -*- codeing = utf-8 -*-
# @Time : 2020/11/28 1:12
# @Author : Cj
# @File : getAmz123KeyWord.py
# @Software : PyCharm

from selenium import webdriver
from time import sleep
from db import MysqlPool

def getKeyword():
    mp = MysqlPool()
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.amz123.com/usatopkeywords-1-1-.htm?rank=0&uprank=0")
    txt = '▶'
    while txt=='▶':
        try:
            data_lists = driver.find_elements_by_xpath('//div[@class="listdata"]')
            for data in data_lists:
                try:
                    keyword = data.find_element_by_xpath('./div').text
                    cur_rank = data.find_element_by_xpath('./div[2]').text
                    last_rank = data.find_element_by_xpath('./div[3]').text
                    sql = "insert into amz123_keyword set keyword=%s,cur_rank=%s,last_rank=%s,add_time=now()"
                    param = [keyword,cur_rank,last_rank]
                    mp.insert(sql,param)
                    print("---%s入库成功---"%keyword)
                except:
                    continue
            sleep(1)
            next_page = driver.find_element_by_xpath('//nav/ul/li[last()]')
            txt = next_page.text
            if next_page.text == '▶':
                next_page.click()
        except:
            continue
    print("采集完毕")
    driver.close()
    driver.quit()



if __name__ == "__main__":
    getKeyword()