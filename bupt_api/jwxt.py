import datetime
import logging
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

from bupt_api.login import auth

JWXT_LOGIN_URL = 'https://jwxt.bupt.edu.cn/caslogin.jsp'
CLASS_URL = 'https://jwxt.bupt.edu.cn/xkAction.do?actionType=6'
QBURL = 'https://jwxt.bupt.edu.cn/gradeLnAllAction.do?type=ln&oper=qbinfo'


@dataclass
class ClassTime:
    start_time: datetime.datetime
    end_time: datetime.datetime


@dataclass
class Class:
    name: str
    teacher: str
    location: str
    weekday: int
    weeks: str
    session: int
    number: int
    time: List[ClassTime]


# 成绩
@dataclass
class ClassScore:
    number: str  # 课程号
    sort_number: str  # 课序号
    name: str  # 课程名
    eng_name: str  # 英文课程名
    credit: float  # 学分
    score: float  # 成绩
    attr: str  # 课程属性


@dataclass
class Term:
    name: str
    class_: List[ClassScore]


class Jwxt(auth):
    session: requests.Session = None

    def __init__(self, username, password):
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
        except AttributeError:
            # no pyopenssl support used / needed / available
            pass
        auth.__init__(self, username, password)
        self.session.get(JWXT_LOGIN_URL)

    def get_pass_score(self):
        pass_score: List[Term] = []
        r = self.session.get(QBURL)
        soup = BeautifulSoup(r.text, 'lxml')
        topic = soup.find_all('table', class_='title')
        details = soup.find_all('table', class_='titleTop2')
        for name, detail in zip(topic, details):
            topic_name = name.find('b').get_text(strip=True)
            scores: List[ClassScore] = []
            for tr in detail.find_all('tr', class_='odd'):
                tds = tr.find_all('td')
                number = tds[0].get_text(strip=True)
                sort_number = tds[1].get_text(strip=True)
                name_ = tds[2].get_text(strip=True)
                eng_name = tds[3].get_text(strip=True)
                credit = float(tds[4].get_text(strip=True))
                attr = tds[5].get_text(strip=True)
                try:
                    score = float(tds[6].get_text(strip=True))
                except ValueError:
                    logging.warning('%s  成绩信息错误！', name_)
                scores.append(
                    ClassScore(number, sort_number, name_, eng_name, credit,
                               attr, score))
            pass_score.append(Term(topic_name, scores))
        return pass_score

    def get_classes(self):
        classes: List[Class] = []
        r = self.session.get(CLASS_URL)
        soup = BeautifulSoup(r.text, 'lxml')

        name = ''
        teacher = ''
        location = ''
        for tr in soup.findAll('tr', class_='odd'):
            time_ = datetime.datetime.strptime('2019-08-26 08:00:00+0800',
                                               '%Y-%m-%d %H:%M:%S%z')  # 开学第一天
            tds = tr.findAll('td')
            try:
                if len(tds) == 18:
                    name = tds[2].get_text(strip=True)
                    teacher = tds[7].get_text(strip=True)
                    weeks_str = tds[11].get_text(strip=True)
                    weekday = int(tds[12].get_text(strip=True))
                    session = int(tds[13].get_text(strip=True))
                    number = int(tds[14].get_text(strip=True))
                    location = tds[17].get_text(strip=True)
                else:
                    weeks_str = tds[0].get_text(strip=True)
                    weekday = int(tds[1].get_text(strip=True))
                    session = int(tds[2].get_text(strip=True))
                    number = int(tds[3].get_text(strip=True))
                    location = tds[6].get_text(strip=True)
            except ValueError:
                logging.warning('%s  没有时间信息！！！', name)
                continue
            class_time = []
            weeks = []
            try:
                weeks = __return_week__(weeks_str)
            except Exception as e:
                logging.error("%s 解析周数错误！！！", name)
                logging.error('周数字符串为： %s', weeks_str)
                logging.error(
                    '请将此issue提交到 http://github.com/WangZeKun/bupt-api')
                logging.error(e)
            for week in weeks:
                start_time = time_ + \
                             datetime.timedelta(days=weekday - 1, weeks=week - 1)
                start_time, end_time = __get_time__(start_time, session,
                                                    number)
                class_time.append(ClassTime(start_time, end_time))
            classes.append(
                Class(name, teacher, location, weekday, weeks_str, session,
                      number, class_time))
        return classes


def __get_time__(start_time, session: int, number: int):
    time_data = {
        1: datetime.timedelta(minutes=0),
        2: datetime.timedelta(minutes=50),
        3: datetime.timedelta(minutes=110),
        4: datetime.timedelta(minutes=160),
        5: datetime.timedelta(minutes=210),
        6: datetime.timedelta(minutes=300),
        7: datetime.timedelta(minutes=350),
        8: datetime.timedelta(minutes=405),
        9: datetime.timedelta(minutes=460),
        10: datetime.timedelta(minutes=515),
        11: datetime.timedelta(minutes=565),
        12: datetime.timedelta(minutes=630),
        13: datetime.timedelta(minutes=680),
        14: datetime.timedelta(minutes=721)
    }
    return start_time + time_data[session], start_time + time_data[
        session + number - 1] + datetime.timedelta(minutes=45)


def __return_week__(s):
    week = []
    index = 0
    flag = 0

    def getnumber(index):
        temp = index
        while temp < len(s) and s[temp].isdigit():
            temp += 1
        num = int(s[index:temp])
        index = temp
        return num, index

    if s[index] == '单':
        index += 3
        flag = 1
    elif s[index] == '双':
        index += 3
        flag = 2
    elif s[index] == '实':
        index += 5
    while len(s) > index and s[index].isdigit():
        start, index = getnumber(index)
        end = start
        if index < len(s):
            print(s[index])
            if s[index] == '-':
                index += 1
                end, index = getnumber(index)
                index += 1
            elif s[index] == '、' or s[index] == ',':
                index += 1
            elif s[index] == "周" and s[index + 1] == "上":
                index += 2
            else:
                raise Exception("invalid str")
        week += list(range(start, end + 1))

    if flag == 2:
        for i in week:
            if i % 2 != 0:
                week.remove(i)
    elif flag == 1:
        for i in week:
            if i % 2 == 0:
                week.remove(i)
    return week
