# coding: utf-8
__author__ = 'chenguo'

import random
import time
import re
import os
import gzip
import StringIO
import json
import threading
import sys
from conf import passwd

class Task(object):
    user_login_param = dict()


class LangYongBoDuan(Task):
    """
    狼用波段碉堡了
    跟着吃肉偷偷地
    """
    status = 1
    leatest_time = int(time.time())*1000
    user_login_param = {
        "areacode": "86",
        "telephone": passwd.xueqiu_user,
        "password": passwd.xueqiu_password,
        "remember_me": "on",
    }
    dest_info  = {
        "path": 'v4/statuses/user_timeline.json',
        "param": {
            "user_id": "8240989798",
            "page": 1,
            "source": "买卖",
        }
    }


    @staticmethod
    def server_forever():
        try:
            while self.status:
                if self.start() != 0:
                    continue
                sleep_sec = random.randint(20,60)
                print "%s秒后重新抓取" % sleep_sec
                time.sleep(sleep_sec)
        except KeyboardInterrupt:
            print "程序退出"
            return

    @staticmethod
    def start():
        data = self.monitor.http_get(self.dest_info["path"], callback=handler_result, **self.dest_info["param"])
        if data is None:
            print "抓取目标页面信息失败"
            notice("抓取目标页面信息失败")
            return 0
        return self.process(data)

    @staticmethod
    def process(data):
        def process_one(item):
            text = item.get('text')
            text = text.encode('utf-8')
            timeStamp = item.get('created_at')/1000
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timeStamp))
            match = re.search(r"(?P<date>(19|20)[0-9]{2}[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])).+?(?P<price>[-+]?\b[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)(?P<action>.+?)</?[a-z][a-z0-9]*[^<>]*>\$(?P<name>.+?)\((?P<code>\w+?\d{6})\).+", text)
            if match:
                price = match.group("price")
                action = match.group("action")
                name = match.group("name")
                code = match.group("code")
                message = "%s 以 %s %s %s %s" % (time_str,price, action, name, code)
                print message
                t = threading.Thread(target=notice, args=(message,))
                t.start()
            else:
                print "匹配出错:%s" % text
                # Exception("not match: %s" % text)
        if not isinstance(data, dict):
            print "解析目标页面信息失败"
            notice("解析目标页面信息失败")
            self.status = 0
            return -1
        operate_list = data.get('statuses', [])
        max = 0
        for operate in operate_list:
            created_at = operate.get('created_at', 0)
            if created_at > self.leatest_time:
                max = created_at if created_at > max else max
                process_one(operate)
            else:
                break
        self.leatest_time = max if self.leatest_time < max else self.leatest_time
        return 0

self = LangYongBoDuan

def gzdecode(data):
    compressedstream = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=compressedstream)
    data2 = gziper.read()   # 读取解压缩后数据
    return data2

def handler_result(data):
    return json.loads(data)


def notice(msg):
    _names = sys.builtin_module_names
    if 'posix' in _names:
        os.system("alert %s" % msg)
    elif 'nt' in _names:
        # todo windows 上的告警
        pass
    #TODO 手机通知
    pass
