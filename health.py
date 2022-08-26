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


class TrangeBar:
    def __init__(self, all_length):
        self.bar = trange(all_length, bar_format="%s{l_bar}{bar}{r_bar}%s" % (Fore.LIGHTBLUE_EX, Fore.RESET))
        self.stop = False

    def end(self):
        self.stop = True

    def loop(self, length, speed):
        for _ in range(length):
            if self.stop: break
            time.sleep(speed * length / 1000)
            self.bar.update(1)

    def update(self, length, times):
        threading.Thread(target=self.loop, args=(length, times), daemon=True).start()


def health_report(username: str, password: str):

    print("当前时间", time.asctime(time.localtime(time.time())))
    print("\033[1;32m" + username + " 开始疫情填报\033[0m")

    try_time: int = 6
    success: bool = False

    for i in range(try_time):
        print("\033[1;32m" + username + " 第" + "一二三四五六"[i] + "次填报开始\033[0m")
        bar = TrangeBar(100)
        try:

            bar.update(30, 5)
            print("\n\033[1;34m步骤 1/5：启动浏览器\033[0m")
            option = webdriver.ChromeOptions()
            option.add_argument("--headless")
            option.add_argument('--log-level=3')
            option.add_argument("--disable-logging")
            option.add_argument("--disable-notifications")
            option.add_argument("--disable-popup-blocking")
            os.environ['WDM_LOG_LEVEL'] = '0'
            warnings.filterwarnings("ignore")
            browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)

            bar.update(10, 10)
            print("\n\033[1;34m步骤 2/5：访问填报网页\033[0m")
            # 不需要从学校网站进一遍
            # browser.get("https://ecampus.nwpu.edu.cn")
            browser.get('''http://yqtb.nwpu.edu.cn/wx/xg/yz-mobile/index.jsp''')
            time.sleep(1)

            bar.update(20, 10)
            print("\n\033[1;34m步骤 3/5：填写账号密码并跳转\033[0m")
            browser.find_elements(by=By.CSS_SELECTOR, value=r'#username')[0].send_keys(username)
            browser.find_elements(by=By.CSS_SELECTOR, value=r'#password')[0].send_keys(password)
            browser.find_elements(by=By.CSS_SELECTOR, value=r'[name=submit]')[0].click()
            time.sleep(3)
            # 新版不需要再进入一次了，会直接跳转到填报
            # browser.get('''http://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp''')

            bar.update(30, 6)
            print("\n\033[1;34m步骤 4/5：确认并提交填报信息\033[0m")
            if len(browser.find_elements(by=By.CSS_SELECTOR, value=r"#layui-layer1")) != 0:
                bar.end()
                print("\033[1;31m" + username + " 第" + "一二三四五六"[i] + "次填报未在规定时间进行，将直接退出\033[0m")
                return
            browser.find_elements(by=By.CSS_SELECTOR, value=r'.weui-btn.weui-btn_primary')[0].click()
            time.sleep(1.5)
            browser.find_elements(by=By.CSS_SELECTOR, value=r'.weui-cells.weui-cells_checkbox')[0].click()
            time.sleep(0.5)
            browser.execute_script("javascript:save()")

            bar.update(10, 15)
            print("\n\033[1;34m步骤 5/5：等待填报完成\033[0m")
            time.sleep(4.5)

            print("\n\033[1;32m" + username + " 疫情填报完成\033[0m")
            success = True

        except Exception as e:
            bar.end()
            print("\n", e, sep="")
            print("\033[1;31m" + username + " 第" + "一二三四五六"[i] + "次填报有误\033[0m")
            time.sleep(2)

        if success:
            break

    if not success:
        print("\033[1;31m" + username + " 今日填均有误，请手动完成\033[0m")


if __name__ == "__main__":
    while True:

        # 可以在运行时手动更新 config.json
        config: dict = json.load(open('./config.json', 'r', encoding='utf-8'))
        start_time = re.split("[:：.]", config[0])
        start_time = int(start_time[0]) * 60 + int(start_time[1])
        for mem in config[1]:
            user, passwd = mem.get("username"), mem.get("password")
            print("\n\033[1;33m开始 " + user + " 的疫情填报\033[0m")
            health_report(user, passwd)
            print()
            time.sleep(2)
        now_time = time.localtime(time.time())
        now_time = now_time.tm_hour * 60 + now_time.tm_min

        if start_time > now_time:
            print("下次填报将等待", (start_time - now_time), "分钟\n")
            time.sleep(60 * (start_time - now_time))
        else:
            print("下次填报将等待", (start_time - now_time + 60 * 24), "分钟\n")
            time.sleep(60 * (start_time - now_time + 60 * 24))


