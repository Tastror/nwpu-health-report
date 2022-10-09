import re
import os
import json
import time
import logging
import warnings
import threading
import logging.handlers
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

    def loop(self, length, time_per_dot):
        for _ in range(length):
            if self.stop: break
            time.sleep(time_per_dot * length / 1000)
            self.bar.update(1)

    def update(self, length, times):
        threading.Thread(target=self.loop, args=(length, times), daemon=True).start()


class LoggerHealth:
    def __init__(self):
        self.logger_health = logging.getLogger("health")
        self.logger_health.setLevel(logging.DEBUG)

        hfh = logging.handlers.RotatingFileHandler(
            'health.log', mode="a", maxBytes=1024*1024, backupCount=2
        )
        rh_formatter = logging.Formatter(
            "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
        )
        hfh.setFormatter(rh_formatter)
        self.logger_health.addHandler(hfh)

        # hsh = logging.StreamHandler(sys.stdout)
        # hsh.setFormatter(rh_formatter)
        # self.logger_health.addHandler(hsh)

    def info(self, *args, **kwargs):
        self.logger_health.info(*args, **kwargs)
        print("\033[1;34mINFO - ", args[0], "\033[0m", sep="")

    def error(self, *args, **kwargs):
        self.logger_health.error(*args, **kwargs)
        print("\033[1;31mERROR - ", args[0], "\033[0m", sep="")

    def debug(self, *args, **kwargs):
        self.logger_health.debug(*args, **kwargs)
        print("\033[1;32mDEBUG - ", args[0], "\033[0m", sep="")

    def warning(self, *args, **kwargs):
        self.logger_health.warning(*args, **kwargs)
        print("\033[1;33mWARN - ", args[0], "\033[0m", sep="")


logger_health = LoggerHealth()


def health_report(username: str, password: str):

    logger_health.warning("当前时间" + time.asctime(time.localtime(time.time())))
    logger_health.info(username + " 开始疫情填报")

    suffix_list = ['', 'fx']
    try_time: int = 6
    success: bool = False

    for i in range(try_time):
        used_suffix = suffix_list[i % 2]

        logger_health.info(username + " 第" + "一二三四五六"[i] + "次填报开始")
        logger_health.debug("suffix = " + ("None" if used_suffix == "" else used_suffix))
        bar = TrangeBar(100)

        try:

            bar.update(20, 8)
            logger_health.info("步骤 1/5：启动浏览器")
            option = webdriver.ChromeOptions()
            option.add_argument("--headless")
            option.add_argument('--log-level=3')
            option.add_argument("--disable-logging")
            option.add_argument("--disable-notifications")
            option.add_argument("--disable-popup-blocking")
            os.environ['WDM_LOG_LEVEL'] = '0'
            warnings.filterwarnings("ignore")
            browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=option)

            bar.update(20, 10)
            logger_health.info("步骤 2/5：访问填报网页")
            browser.get("""https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp""")
            use_password = browser.find_elements(by=By.CSS_SELECTOR, value=r'[role=menubar] [role=menuitem]:last-child')[0]
            use_password.click()

            bar.update(20, 10)
            logger_health.info("步骤 3/5：填写账号密码并跳转")
            browser.find_elements(by=By.CSS_SELECTOR, value=r'#username')[0].send_keys(username)
            browser.find_elements(by=By.CSS_SELECTOR, value=r'#password')[0].send_keys(password)
            browser.find_elements(by=By.CSS_SELECTOR, value=r"#fm1 [name=button]")[0].click()
            time.sleep(1.5)
            phone_code_needed = browser.find_elements(by=By.CSS_SELECTOR, value=r'div[role=dialog]')
            if len(phone_code_needed) == 0:
                logger_health.info("很幸运，这次不需要验证码")
            else:
                logger_health.warning("需要验证码，请手动处理")
                # 采用邮件方式处理
                # other_method = browser.find_elements(by=By.CSS_SELECTOR, value=r'div[role=dialog] img.safe-icon')[0]
                # other_method.click()
                send_phone_code = browser.find_elements(by=By.CSS_SELECTOR, value=r'div[role=dialog] .code-wrap > button')[0]
                input("按回车开始获取验证码: (Enter here) ")
                logger_health.warning("正在获取验证码")
                send_phone_code.click()
                phone_code = input("请输入得到的验证码: ")
                input_area = browser.find_elements(by=By.CSS_SELECTOR, value=r'div[role=dialog] .code-wrap input')[0]
                input_area.send_keys(phone_code)
                confirm_button = browser.find_elements(by=By.CSS_SELECTOR, value=r'div[role=dialog] .el-dialog__footer button')[0]
                confirm_button.click()
                time.sleep(1.5)
            browser.get('''http://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp''')
            time.sleep(0.5)

            bar.update(20, 6)
            logger_health.info("步骤 4/5：确认并提交填报信息")
            if len(browser.find_elements(by=By.CSS_SELECTOR, value=r'#rbxx_div .page__top2 .page__title i')) != 0:
                text = browser.find_elements(by=By.CSS_SELECTOR, value=r'#rbxx_div .page__top2 .page__title i')[0] \
                    .get_attribute("innerText")
                logger_health.debug("填报提醒内容：" + text)
                if "您已提交今日填报" in text:
                    logger_health.warning("今日已填报，将不再继续进行填报～")
                    bar.end()
                    logger_health.info(username + " 疫情填报完成")
                    success = True
                    break
            if len(browser.find_elements(by=By.CSS_SELECTOR, value=r"#layui-layer1")) != 0:
                logger_health.warning(username + " 第" + "一二三四五六"[i] + "次填报未在规定时间进行，将强制填报")
                browser.find_elements(by=By.CSS_SELECTOR, value=r'.layui-layer-btn0')[0].click()
                time.sleep(1)
            browser.execute_script("javascript:go_sub" + used_suffix + "()")
            time.sleep(1.5)
            browser.find_elements(by=By.CSS_SELECTOR, value=r'.weui-cells.weui-cells_checkbox')[0].click()
            time.sleep(0.5)
            browser.execute_script("javascript:save" + used_suffix + "()")

            bar.update(20, 8)
            logger_health.info("步骤 5/5：等待填报完成")
            time.sleep(4.5)

            logger_health.info(username + " 疫情填报完成")
            success = True

        except Exception as e:
            bar.end()
            logger_health.error(e)
            logger_health.error(username + " 第" + "一二三四五六"[i] + "次填报有误")
            time.sleep(2)

        if success:
            break

    if not success:
        logger_health.error(username + " 今日填报均有误，请手动完成")


if __name__ == "__main__":
    while True:

        # 可以在运行时手动更新 config.json
        config: dict = json.load(open('./config.json', 'r', encoding='utf-8'))
        start_time = re.split("[:：.]", config.get("time", "6:00"))
        start_time = int(start_time[0]) * 60 + int(start_time[1])
        users = config.get("users", [])

        logger_health.warning("共有 " + str(len(users)) + " 人等待填报")
        index = 1
        for mem in users:
            logger_health.warning("当前填报人次 " + str(index) + "/" + str(len(users)))
            index += 1
            user, passwd = mem.get("username"), mem.get("password")
            logger_health.info("开始 " + user + " 的疫情填报")
            health_report(user, passwd)
            time.sleep(2)

        now_time = time.localtime(time.time())
        now_time = now_time.tm_hour * 60 + now_time.tm_min
        time_next = start_time - now_time if start_time > now_time else start_time - now_time + 60 * 24
        logger_health.info("下次填报将等待 " + str(time_next) + " 分钟")
        time.sleep(60 * time_next)
