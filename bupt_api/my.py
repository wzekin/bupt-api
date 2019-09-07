from typing import List
import re
import json
from bs4 import BeautifulSoup
from dataclasses import dataclass
import datetime
import requests
from bupt_api.login import auth

# MY_LOGIN_URL = ""
LECTURE_URL = "http://my.bupt.edu.cn/detach.portal?.p=Znxjb20ud2lzY29tLnBvcnRhbC5jb250YWluZXIuY29yZS5pbXBsLlBvcnRsZXRFbnRpdHlXaW5kb3d8cGU3MjJ8dmlld3xub3JtYWx8YWN0aW9uPWxlY3R1cmVCcm93c2Vy"
MONEY_URL = "http://my.bupt.edu.cn/pnull.portal?.pen=pe745&.pmn=view&action=ajaxQuery&daibanBeanId=66ac7576-6a55-48eb-9e4c-8390864eea2b"
BOOK_URL = "http://my.bupt.edu.cn/pnull.portal?.pen=pe745&.pmn=view&action=ajaxQuery&daibanBeanId=1e163e33-48a9-45b7-ae61-07c5acbe4566"


@dataclass
class Lecture:
    name: str
    url: str
    time: datetime.datetime


class My(auth):
    session: requests.Session = None
    lectures: List[Lecture] = []

    def __init__(self, username: str, password: str):
        auth.__init__(self, username, password)
        # self.session.get(MY_LOGIN_URL)

    def get_lecture(self):
        r = self.session.post(LECTURE_URL)
        soup = BeautifulSoup(r.text, "lxml")
        for li in soup.find('ul', class_="newslist list-unstyled").find_all('li'):
            a = li.find('a')
            name = a.get_text(strip=True)
            url = a.href
            time = datetime.datetime.strptime(name[0:16], '%Y-%m-%d %H:%M')
            self.lectures.append(Lecture(name, url, time))
        return self.lectures

    def get_after_lecture(self):
        return list(filter(lambda l: l.time > datetime.datetime.now(), self.get_lecture()))

    def get_money_info(self):
        r = self.session.get(MONEY_URL)
        obj = json.loads(r.content.decode('utf-8'))
        return float(re.search(r'>(.*)<', obj['description']).group(1))

    def get_book_info(self):
        r = self.session.get(BOOK_URL)
        obj = json.loads(r.content.decode('utf-8'))
        return obj['description']
