import datetime
import re
import json
import logging
import requests

from bupt_api.jwxt import Class, ClassTime

JWGL_APP_URL = 'http://jwgl.bupt.edu.cn/app.do'

term_start_time = datetime.datetime.strptime('2020-02-23 00:00:00+0800',
                                             '%Y-%m-%d %H:%M:%S%z')  # 开学第一天


class Jwql:
    session: requests.Session = None
    token: str
    username: str

    def __init__(self, username, password):
        self.session = requests.Session()
        self.username = username
        r = self.session.get(JWGL_APP_URL,
                             params={
                                 'method': 'authUser',
                                 'xh': username,
                                 'pwd': password
                             })
        data = json.loads(r.text)
        if not data["success"]:
            raise Exception(data["msg"])
        self.token = data["token"]

    def get_classes(self, xnxqid, term_start_time):
        classes = []
        data = []
        # 由于只能获取到每周的课程，所以只能把每一周都遍历一遍。。。
        for i in range(0, 21):
            r = self.session.get(JWGL_APP_URL,
                                 headers={"token": self.token},
                                 params={
                                     'method': 'getKbcxAzc',
                                     'xh': self.username,
                                     'xnxqid': xnxqid,
                                     'zc': i
                                 })
            data_ = json.loads(r.text)
            for d in data_:
                if d not in data:
                    data.append(d)
        for class_ in data:
            name = class_["kcmc"]
            location = class_["jsmc"]
            teacher = class_["jsxm"]
            class_time = []
            sjbz = int(class_["sjbz"])
            if sjbz == 1:
                weeks_str = class_["kkzc"] + "(单周)"
            elif sjbz == 2:
                weeks_str = class_["kkzc"] + "(双周)"
            else:
                weeks_str = class_["kkzc"]
            weekday = int(class_["kcsj"][0])
            session = int(class_["kcsj"][1:3])
            number = int(class_["kcsj"][3:5]) - session
            try:
                weeks = __return_week__(class_["kkzc"], sjbz)
            except Exception as e:
                logging.error("%s 解析周数错误！！！", name)
                logging.error('周数字符串为： %s', weeks_str)
                logging.error(
                    '请将此issue提交到 http://github.com/WangZeKun/bupt-api')
                logging.error(e)

            for week in weeks:
                time = term_start_time + datetime.timedelta(days=weekday - 1,
                                                            weeks=week - 1)
                regex = re.compile(r'([0-9]{2}):([0-9]{2})')
                start = regex.match(class_["kssj"])
                start_time = time + datetime.timedelta(
                    hours=int(start.group(1)), minutes=int(start.group(2)))
                end = regex.match(class_["jssj"])
                end_time = time + datetime.timedelta(hours=int(end.group(1)),
                                                     minutes=int(end.group(2)))
                class_time.append(ClassTime(start_time, end_time))
            classes.append(
                Class(name, teacher, location, weekday, weeks_str, session,
                      number, class_time))
        return classes


def __return_week__(s, sjbz):
    # sjbz具体意义未知，据观察值为1时本课单周上，2时双周上
    week = []
    s = s.split(",")
    for i in s:
        match = re.match(r'([0-9]*)-([0-9]*)', i)
        if match:
            for j in range(int(match.group(1)), int(match.group(2)) + 1):
                week.append(j)
        else:
            week.append(int(i))

    if sjbz == 2:
        for i in week:
            if i % 2 != 0:
                week.remove(i)
    elif sjbz == 1:
        for i in week:
            if i % 2 == 0:
                week.remove(i)
    return week
