# -*- codeing = utf-8 -*-
# @Time : 2020/10/1 19:39
# @Author : Cj
# @File : amzAction.py
# @Software : PyCharm

from selenium import webdriver
import string,zipfile,os
from time import sleep

# 打包Google代理插件
def create_proxyauth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_path=None):
    if plugin_path is None:
        file = 'C:/py_file/proxyauth'
        if not os.path.exists(file):
            os.mkdir(file)
        plugin_path = file + '/%s_%s@%s_%s.zip' % (proxy_username, proxy_password, proxy_host, proxy_port)
        # plugin_path = '/2.zip'

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


def test():
    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host="196.245.186.197",
        proxy_port=12345,
        proxy_username="pethan",
        proxy_password="52renren",
        scheme='http'
    )
    options = webdriver.ChromeOptions()
    options.add_extension(proxyauth_plugin_path)
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    # options.add_argument('blink-settings=imagesEnabled=false')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.baidu.com/")
    sleep(10000)

if __name__ == "__main__":
    # a = 'B08DTP8TZY,B087R2S3H6,B088HDWJSS'
    # print('B088HDWJSS' in a)
    os.system("taskkill /f /im chrome.exe /t")
    # test()

    # s = '123'
    # m = hashlib.md5(s.encode())
    # print(m.hexdigest())
    #
    # m = hashlib.sha3_224(s.encode())  # 长度是224
    # print(m.hexdigest())
    #
    # m = hashlib.sha3_256(s.encode())  # 长度是256
    # print(m.hexdigest())
    #
    # m = hashlib.sha3_512(s.encode())  # 长度是512
    # print(m.hexdigest())

    # ua = UserAgent().chrome
    # options = webdriver.ChromeOptions()
    # options.add_argument("user-agent=" + ua)
    # options.add_argument("--start-maximized")
    # # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("log-level=3")
    # # options.add_argument('blink-settings=imagesEnabled=false')
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # driver = webdriver.Chrome(options=options)
    # driver.get("https://www.baidu.com")
    # WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, 'su')))
    # cookies = [{"domain": ".amazon.com", "expirationDate": 1634841433.047612, "hostOnly": False, "httpOnly": False,
    #             "name": "ubid-main", "path": "/", "sameSite": "unspecified", "secure": True, "session": False,
    #             "storeId": None, "value": "132-8813534-9194430"},
    #            {"domain": ".amazon.com", "expirationDate": 1634841419.347564, "hostOnly": False, "httpOnly": False,
    #             "name": "session-token", "path": "/", "sameSite": "unspecified", "secure": True, "session": False,
    #             "storeId": None,
    #             "value": "bklqyXNcY2otHUrB0UC7lT3W06X4gp0jdezDNDRHh2erSpsdmsW+dIVeX1SgTkvpZCkF4m7Q7OzI9PGWB+oYC58Eqz6m1ALaqcwGi0tj0hZHeJpqolKUESA+rSmnK9zcN0ee+Ij4zSkL2QAmo52Xlc7r1wUWfxmNu0HGOkzWCVfHZXTCEPlamVQGgjS1sgW04UiCCHlJwXSwbrK/VAHJEqZs6htE4asMT0Xyh+xXLDuv7uBO8qEBvU93+RawA6NYI9pk13lAYn70Yzc3TcR/gA=="},
    #            {"domain": ".amazon.com", "expirationDate": 1634461817.464778, "hostOnly": False, "httpOnly": False,
    #             "name": "i18n-prefs", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "USD"},
    #            {"domain": ".amazon.com", "expirationDate": 1634461817.464754, "hostOnly": False, "httpOnly": False,
    #             "name": "x-main", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "\"VRbmyyTVH@lveo2DxwcmgrjIvVrm7qyzrE2RdThu0TZ2Nnt8f9uIO8qepf9pmrE4\""},
    #            {"domain": "www.amazon.com", "expirationDate": 1633545423, "hostOnly": True, "httpOnly": False,
    #             "name": "csm-hit", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "tb:s-76JPR4REJEG0TFX5E92S|1603305423259&t:1603305423909&adb:adblk_no"},
    #            {"domain": ".www.amazon.com", "expirationDate": 1608197420, "hostOnly": False, "httpOnly": False,
    #             "name": "csd-key", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None,
    #             "value": "eyJ2IjoxLCJraWQiOiI4ZmNjYzIiLCJrZXkiOiJOclh4Vk9NNlFJNWhYNUU0Vk5LQUlDM0wzUjdUNkNHRjRmRDRqN3AwYkwwOWdvU1lvTWFEeWVmZEx6cVUreDVZZTJHWkVMVjBPZHFtLzlSWXlBanlBYmVsTXR2cmdUMkFLemswazdseU1xMWtjeG1YbFViWER6UHkzM1FZUHYzaHhKWmtDQWMvemVPS0VEdUNYdWhWNEZDM1pSemZ3UGdta0h4d2l1SW11Q05DL3lnNk03RC9hekFOVlhNblNVbVd0ZExjUktFNHRTQjczcnZseFRrUlRFVVVNMGp5cjN6M1NydzZGcjJTV0luYmREaVg0K0ppVzhGcGhUOWJldFlmWWNUMEp3T0V5UWRyc01CamxiRFhUVFFkNlRWU05GRkJDb2FHaTBBSVlqcGZUQW9FU0dOMlk4cGI2ZHJPQmswcUpEK2FUcWpLaS80amo1QWhJTXl3WEE9PSJ9"},
    #            {"domain": ".amazon.com", "expirationDate": 1634626988.016198, "hostOnly": False, "httpOnly": True,
    #             "name": "sp-cdn", "path": "/", "sameSite": "unspecified", "secure": True, "session": False,
    #             "storeId": None, "value": "\"L5Z9:CA\""},
    #            {"domain": ".amazon.com", "expirationDate": 1634841433.047716, "hostOnly": False, "httpOnly": False,
    #             "name": "session-id-time", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "2082787201l"},
    #            {"domain": ".amazon.com", "expirationDate": 1634461815.227964, "hostOnly": False, "httpOnly": True,
    #             "name": "at-main", "path": "/", "sameSite": "unspecified", "secure": True, "session": False,
    #             "storeId": None,
    #             "value": "Atza|IwEBIIByFl3fO_epDc_IgeQmFoX01aOVdjk5pO0DjqFO588DFCgjQUrnfrFY4nj1xZrVhpwshh2PCPTvDb0YXgVqZueKhJHdQ4UJiblJE1x4VR2RmOsuSbq7jbLy5dh_-YvwZhX31TP65hf7XLzAU6cmwp-x-zBIynm4Wne7rzu6G3EH4JYE37ZIvbKsJ24HTS-LIbzhkkuJUFl6JUfNF1pIYAwa"},
    #            {"domain": ".amazon.com", "expirationDate": 1697212874, "hostOnly": False, "httpOnly": False,
    #             "name": "s_dslv", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "1602604874334"},
    #            {"domain": ".amazon.com", "expirationDate": 2016336910, "hostOnly": False, "httpOnly": False,
    #             "name": "s_vnum", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "2016336910355%26vn%3D5"},
    #            {"domain": ".amazon.com", "expirationDate": 2082787202.081333, "hostOnly": False, "httpOnly": False,
    #             "name": "lc-main", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "en_US"},
    #            {"domain": ".amazon.com", "expirationDate": 2034604874, "hostOnly": False, "httpOnly": False,
    #             "name": "s_nr", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "1602604874325-Repeat"},
    #            {"domain": ".amazon.com", "expirationDate": 1743088530, "hostOnly": False, "httpOnly": False,
    #             "name": "s_pers", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None,
    #             "value": "%20s_fid%3D0E27D31BD56383E9-3CFD0121F9F53866%7C1743088530834%3B%20s_dl%3D1%7C1585323930836%3B%20gpv_page%3DUS%253ASD%253ASOA-home%7C1585323930844%3B%20s_ev15%3D%255B%255B%2527www.baidu.com%2527%252C%25271584108648930%2527%255D%252C%255B%2527SCSOAStriplogin%2527%252C%25271584108685311%2527%255D%252C%255B%2527SCHelpUSSOA-header%2527%252C%25271585322130850%2527%255D%255D%7C1743088530850%3B"},
    #            {"domain": ".amazon.com", "expirationDate": 1634461815.228004, "hostOnly": False, "httpOnly": True,
    #             "name": "sess-at-main", "path": "/", "sameSite": "unspecified", "secure": True, "session": False,
    #             "storeId": None, "value": "\"j58QvyLE4MrctxHR5TJl9z5ybqDxs1lLaviUqqlBo+c=\""},
    #            {"domain": ".amazon.com", "expirationDate": 1634841433.047799, "hostOnly": False, "httpOnly": False,
    #             "name": "session-id", "path": "/", "sameSite": "unspecified", "secure": True, "session": False,
    #             "storeId": None, "value": "130-2343992-9258319"},
    #            {"domain": ".amazon.com", "expirationDate": 1634461815.228034, "hostOnly": False, "httpOnly": True,
    #             "name": "sst-main", "path": "/", "sameSite": "unspecified", "secure": True, "session": False,
    #             "storeId": None,
    #             "value": "Sst1|PQGmODmmRVTr4wTLLX7mC_VMCe0J3P52_mD3AvlkxGjwTeD5t2uFDgSPioYSnBPz5FAKe4eEMCynHWDP9mbjfHWeq27W_XPxCj7PjidcMlr7TLPMy0pnr6s_mUeQvv8G8ODlmUTJetjg2a8lcjR-x5paCvCJByvRtwGT37gKFa-ayxKUJsZbAv09O-TDHtkNVYqU3QxSvirmTT0eZCb2tzS63lFWSxGyP6BmOZP8NymMfpMUqe9XOMMgR02jZ_WwUy0ZYxmDo3MoC-Ygd_ernXnlFasORJS71q6HnPlois37w1Q"},
    #            {"domain": ".amazon.com", "expirationDate": 2082787202.245597, "hostOnly": False, "httpOnly": False,
    #             "name": "ubid-acbus", "path": "/", "sameSite": "unspecified", "secure": False, "session": False,
    #             "storeId": None, "value": "135-5461869-9698219"}]
    # for cookie in cookies:
    #     try:
    #         cookie.pop('sameSite')
    #     except:
    #         pass
    #     driver.add_cookie(cookie_dict=cookie)
    # driver.get("https://www.amazon.com")
    # while True:
    #     sleep(5)
    #     print(driver.get_cookies())
