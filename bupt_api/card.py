from typing import List
from dataclasses import dataclass
from typing import Dict
import requests
from bs4 import BeautifulSoup
from pprint import pprint

from bupt_api.login import auth

CARD_LOGIN_URL = 'http://10.3.255.131:85/SSOLogin.aspx'
CARD_LOGIN_URL2 = 'http://10.3.255.131/SSOLogin.aspx'
CONSUME_INFO_URL = 'http://10.3.255.131/User/ConsumeInfo.aspx'


@dataclass()
class Cost:
    time: str
    desc: str
    cost: float
    balance: float
    location: str


class Card(auth):
    session: requests.Session = None
    request_data: Dict = {}

    def __init__(self, username: str, password: str):
        auth.__init__(self, username, password)
        r = self.session.get(CARD_LOGIN_URL)
        soup = BeautifulSoup(r.text, "lxml")
        request_data = {}
        for target in soup.find_all("input", attrs={'type': 'hidden'}):
            request_data[target.attrs["name"]] = target.attrs["value"]

        request_data.pop("__VIEWSTATE")
        request_data.pop("__VIEWSTATEGENERATOR")
        self.session.post(CARD_LOGIN_URL2, data=request_data,
                          headers={'Content-Type': 'application/x-www-form-urlencoded',
                                   'Origin': 'http://10.3.255.131:85',
                                   'Upgrade-Insecure-Requests': "1",
                                   })

    def get_costs(self, start_time: str, end_time: str):
        self.__get_base_consume_info__()
        costs, count = self.__init_cost_page__(start_time, end_time)
        for i in range(2, count):
            costs += self.__get_one_page_costs__(start_time, end_time, i)
        return costs

    def __get_base_consume_info__(self):
        r = self.session.get(CONSUME_INFO_URL)
        soup = BeautifulSoup(r.text, "lxml")
        for target in soup.find_all("input", attrs={'type': 'hidden'}):
            self.request_data[target.attrs["name"]] = target.attrs["value"]
        self.request_data["ctl00$ContentPlaceHolder1$rbtnType"] = 0

    def __init_cost_page__(self, start_time: str, end_time: str):
        self.request_data["ctl00$ContentPlaceHolder1$btnSearch"] = "查 询"
        self.request_data["ctl00$ContentPlaceHolder1$txtStartDate"] = start_time
        self.request_data["ctl00$ContentPlaceHolder1$txtEndDate"] = end_time
        self.request_data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$gridView$ctl01$SortBt"
        return self.__parse_cost_page__(True)

    def __parse_cost_page__(self, getCount=False):
        costs: List[Cost] = []
        r = self.session.post(CONSUME_INFO_URL, self.request_data,
                              headers={'Content-Type': 'application/x-www-form-urlencoded',
                                       'Origin': 'http://10.3.255.131:85',
                                       'Upgrade-Insecure-Requests': "1",
                                       })
        soup = BeautifulSoup(r.text, "lxml")
        for target in soup.find_all("input", attrs={'type': 'hidden'}):
            self.request_data[target.attrs["name"]] = target.attrs["value"]
        for tr in soup.find('table', class_="GridViewStyle").find_all('tr')[1:]:
            try:
                tds = tr.find_all('td')
                time = tds[0].getText(strip=True)
                desc = tds[1].getText(strip=True)
                cost = float(tds[2].getText(strip=True))
                balance = float(tds[3].getText(strip=True))
                location = tds[6].getText(strip=True)
                costs.append(Cost(time, desc, cost, balance, location))
            except:
                break
        if getCount:
            return costs, len(soup.find_all('a', class_='aspnetpager'))
        else:
            return costs

    def __get_one_page_costs__(self, start_time: str, end_time: str, page: int = 1):
        try:
            self.request_data.pop("ctl00$ContentPlaceHolder1$btnSearch")
        except:
            pass
        self.request_data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$AspNetPager1"
        self.request_data["__EVENTARGUMENT"] = page
        self.request_data["ctl00$ContentPlaceHolder1$txtStartDate"] = start_time
        self.request_data["ctl00$ContentPlaceHolder1$txtEndDate"] = end_time
        return self.__parse_cost_page__()
