import requests
from bs4 import BeautifulSoup

AUTHURL = 'https://auth.bupt.edu.cn/authserver/login'


class auth:
    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.login(username, password)

    def login(self, username, password):
        r = self.session.get(AUTHURL)
        soup = BeautifulSoup(r.text, 'lxml')
        data = {}
        for i in soup.find("div", class_='loginbox').findAll("input", type='hidden'):
            data[i.attrs['name']] = i.attrs['value']
        data['username'] = username
        data['password'] = password
        r = self.session.post(AUTHURL, data=data, allow_redirects=False)
