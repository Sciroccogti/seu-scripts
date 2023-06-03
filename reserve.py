import datetime
import json
import logging
from random import random
import ssl
import threading
import urllib
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from time import sleep

import ddddocr

import config
import urls
from utils.login import login

lock = threading.Lock()


def reserve(ocr):
    ssl._create_default_https_context = ssl._create_unverified_context

    card_num = config.card_num
    logging.debug(card_num)
    logging.debug("请输入密码:")
    password = config.password
    logging.debug('*'*len(password))
    logging.debug("开始登陆")
    s = login(card_num, password)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    res = s.get(urls.res_val_image, headers=headers, allow_redirects=True, timeout=10)
    res = s.get(str(res.content).split(".href='")
                [-1].split("'</script>")[0], headers=headers, timeout=10)
    valid_s = ocr.classification(res.content)

    postdata = {
        'ids': '',
        'useTime': config.reserve_data['reservetime'],
        'itemId': config.reserve_data['item'],
        'allowHalf': 2,
        'validateCode': valid_s,
        'phone': config.reserve_data['phone'],
        'remark': '',
        'useUserIds': '',
    }

    data = urllib.parse.urlencode(postdata).encode('utf-8')

    res = s.post(urls.res_url, data=data,
                 headers=headers, allow_redirects=False, timeout=10)
    logging.debug(res.status_code)
    logging.debug(res.text)
    resJson = json.loads(res.text)
    if 'sucuss' in resJson.keys():
        logging.info(resJson['sucuss'])
        return True
    else:
        logging.error(resJson)
        return False


def iter():
    global success
    count = 0
    ocr = ddddocr.DdddOcr(show_ad=False)
    _success = False
    while(count < 50):
        try:
            _success = reserve(ocr)
            # print(threading.currentThread().ident)
        except:
            pass
        count += 1
        with lock:
            if success:
                break
            elif _success:
                success = _success
                break


if __name__ == '__main__':
    global success
    logging.basicConfig(level=logging.DEBUG, filename="reserve.log",
                        format="%(asctime)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s")

    now_time = datetime.datetime.now()
    # 获取启动时间
    next_time = datetime.datetime.strptime(
        config.reserve_data['reservetime'][:10], "%Y-%m-%d")  # 获取要预约的日期，初始为0点
    next_time = next_time + datetime.timedelta(days=-2)  # 提前两天预约
    next_time = next_time + datetime.timedelta(hours=+7, minutes=+59, seconds=+58) # 07:59:58 启动
    print("启动时间：", next_time)
    print("预约时间：", config.reserve_data['reservetime'])

    # 获取距离启动时间，单位为秒
    timer_start_time = (next_time - now_time).total_seconds()
    if timer_start_time > 0:
        logging.info("睡眠 %d 秒" % timer_start_time)
        sleep(timer_start_time)

    success = False
    pool = ThreadPoolExecutor(max_workers=config.thread_num)
    tasks_ = [pool.submit(iter) for i in range(config.thread_num)]
    wait(tasks_, return_when=ALL_COMPLETED)
