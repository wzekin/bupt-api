import requests
from bs4 import BeautifulSoup

AUTHURL = 'https://auth.bupt.edu.cn/authserver/login'


class auth:
    def __init__(self, username: str, password: str):
        self.session = requests.Session()
        self.login(username, password)

    def login(self, username, password):
        r = self.session.get(AUTHURL, headers={
            'authority': 'auth.bupt.edu.cn',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'sec-fetch-site': 'none',
            'referer': 'https://auth.bupt.edu.cn/authserver/userAttributesEdit.do',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'cookie': 'JSESSIONID=0000h0MZn1zUHK1vm2faeWFM0DP:19kmg9ok9',
        })
        soup = BeautifulSoup(r.text, 'lxml')
        data = {}
        for i in soup.find("div", class_='loginbox').findAll("input", type='hidden'):
            data[i.attrs['name']] = i.attrs['value']
        data['username'] = username
        data['password'] = password
        print(111)
        r = self.session.post(AUTHURL, data=data, allow_redirects=False)
        print(r.text)
