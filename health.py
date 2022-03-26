import re
import os
import json
import time
import warnings
import threading
from tqdm import trange
from colorama import Fore
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class trange_bar:
    def __init__(self, all_length):
        self.bar = trange(all_length, bar_format="%s{l_bar}{bar}{r_bar}%s" % (Fore.LIGHTBLUE_EX, Fore.RESET))
        self.stop = False

    def end(self):
        self.stop = True

    def loop(self, length, times):
        for _ in range(length):
            if self.stop: break
            time.sleep(times)
            self.bar.update(1)

    def update(self, length, times):
        threading.Thread(target=self.loop, args=(length, times), daemon=True).start()


def health_report(username: str, password: str):
    print(time.asctime(time.localtime(time.time())))
    print("\033[1;32m开始疫情填报\033[0m")
    bar = trange_bar(100)
    try:
        bar.update(35, 0.2)
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        option.add_argument('--log-level=3')
        option.add_argument("--disable-logging")
        option.add_argument("--disable-notifications")
        option.add_argument("--disable-popup-blocking")
        os.environ['WDM_LOG_LEVEL'] = '0'
        warnings.filterwarnings("ignore")
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)
        browser.get("https://ecampus.nwpu.edu.cn")
        bar.update(20, 0.25)
        time.sleep(1)
        browser.find_element(by=By.CSS_SELECTOR, value=r'#username').send_keys(username)
        browser.find_element(by=By.CSS_SELECTOR, value=r'#password').send_keys(password)
        browser.find_element(by=By.CSS_SELECTOR, value=r'[name=submit]').click()
        bar.update(20, 0.1)
        browser.get('''http://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp''')
        browser.get('''http://yqtb.nwpu.edu.cn/wx/ry/jrsb_js.jsp''')
        browser.execute_script('javascript:go_subfx();')
        browser.find_element(by=By.CSS_SELECTOR, value=r'#brcn+i').click()
        browser.execute_script('javascript:savefx();')
        bar.update(25, 0.1)
        time.sleep(3)
        print("\033[1;32m疫情填报完成\033[0m")
    except Exception as e:
        bar.end()
        print(e)
        print("\033[1;31m今日填报有误，请手动完成\033[0m")


if __name__ == "__main__":
    while True:

        # 可以在运行时手动更新 config.json
        config: dict = json.load(open('./config.json', 'r', encoding='utf-8'))
        user, passwd = config["username"], config["password"]
        start_time = re.split("[:：.]", config.get("time", "0:30"))
        start_time = int(start_time[0]) * 60 + int(start_time[1])
        health_report(user, passwd)
        now_time = time.localtime(time.time())
        now_time = now_time.tm_hour * 60 + now_time.tm_min

        if start_time > now_time:
            print("下次填报将等待", (start_time - now_time), "分钟\n")
            time.sleep(60 * (start_time - now_time))
        else:
            print("下次填报将等待", (start_time - now_time + 60 * 24), "分钟\n")
            time.sleep(60 * (start_time - now_time + 60 * 24))


