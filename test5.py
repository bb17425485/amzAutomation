# -*- codeing = utf-8 -*-
# @Time : 2020/11/20 10:28
# @Author : Cj
# @File : test5.py
# @Software : PyCharm

import time,string,zipfile,os
from selenium import webdriver

def create_proxyauth_extension(proxy_host, proxy_port,proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
    """Proxy Auth Extension
    args:
        proxy_host (str): domain or ip address, ie proxy.domain.com
        proxy_port (int): port
        proxy_username (str): auth username
        proxy_password (str): auth password
    kwargs:
        scheme (str): proxy scheme, default http
        plugin_path (str): absolute path of the extension

    return str -> plugin_path
    """
    if plugin_path is None:
        file='./chrome_proxy_helper'
        if not os.path.exists(file):
            os.mkdir(file)
        plugin_path = file+'/%s_%s@%s_%s.zip'%(proxy_username,proxy_password,proxy_host,proxy_port)

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = string.Template(
    """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "${scheme}",
                host: "${host}",
                port: parseInt(${port})
              },
              bypassList: ["foobar.com"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "${username}",
                password: "${password}"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path


if __name__=='__main__':
    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host="89.37.64.84",
        proxy_port=12345,
        proxy_username="pethan",
        proxy_password="52renren",
        scheme='http'
    )
    options = webdriver.ChromeOptions()
    #浏览器最大化
    options.add_argument("--start-maximized")
    #增加扩展
    options.add_extension(proxyauth_plugin_path)
    driver = webdriver.Chrome(chrome_options=options)
    driver.get("http://httpbin.org/ip")
    # driver.get('http://ip138.com/')
    # driver.get('https://www.google.com.hk/search?q=%E6%B8%A4%E6%B5%B7%E9%87%91%E6%8E%A7&safe=strict&tbs=sbd:1&tbm=nws&ei=&start=10&sa=N&biw=&bih=&dpr=1')
    # print(driver.page_source)
    time.sleep(10)
    driver.quit()