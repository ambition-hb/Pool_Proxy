# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import urllib2
import socket
from mongodb import MG
from pymongo import MongoClient

class ProxyGetter:

    def __init__(self):

        self.headers = {
                'Accept': 'textml,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24',
            }

        self.IP_list = []
        self.active_proxy_ip = []
        self.active_num = 0



    #66免费代理http://www.66ip.cn/pt.html
    def getProxy_2(self):

        init_url = r'http://www.66ip.cn/nmtq.php?getnum=800&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=1&proxytype=2&api=66ip'

        r = requests.get(init_url, headers=self.headers)
        #print r.status_code

        for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', r.content):
            IP_format = r'http://' + proxy
            self.IP_list.append({'https': IP_format})
        print('66代理获取IP结束...')

    #西刺代理http://www.xicidaili.com/nn/
    def getProxy_3(self, page=4):

        init_url = r'http://www.xicidaili.com/nn/'

        for i in range(1, page+1):
            html = requests.get(init_url + str(i), headers=self.headers)
            time.sleep(1)
            #print html.status_code
            soup = BeautifulSoup(html.content, "lxml")

            table = soup.find('table', id="ip_list")
            for row in table.findAll("tr"):
                cells = row.findAll("td")
                tmp = []
                for item in cells:
                    tmp.append(item.find(text=True))
                try:
                    tmp2 = tmp[1:2][0]
                    tmp3 = tmp[2:3][0]
                    IP = 'http://' + tmp2 + ":" + tmp3
                    self.IP_list.append({'https': IP})

                except Exception as e:
                    pass

        print('西刺代理获取IP结束...')

    def probe_proxy_ip(self, proxy_ip):
        """代理检测"""
        proxy = urllib2.ProxyHandler(proxy_ip)
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        socket.setdefaulttimeout(3)
        flag = True
        while flag:
            try:
                #http://www.xjtu.edu.cn/
                #https://www.baidu.com
                html = urllib2.urlopen('http://www.xjtu.edu.cn')
                if html:
                    self.active_proxy_ip.append(proxy_ip.get('https'))
                    print(proxy_ip)
                    return True
                    flag = False
                else:
                    print('代码出错')
                    return False
            except Exception as e:
                print('出错' + str(e))
                return False

    def get_avtive_proxy(self):

        mongo = MG()
        #self.getProxy_1()
        self.getProxy_2()
        self.getProxy_3()

        proxy_list = []
        data_list = []
        for proxy in self.IP_list:
            self.probe_proxy_ip(proxy)
        #去重
        proxy_list = list(set(self.active_proxy_ip))

        print('IP池验证结束...')
        print('共获取有效代理数：' + str(len(self.active_proxy_ip)))
        self.active_num = len(self.active_proxy_ip)

        for i in xrange(len(proxy_list)):
            data_list.append({'proxy':{'http':proxy_list[i]}})
            mongo.db.proxy_new.insert({'proxy':{'http':proxy_list[i]}})

        #新加----调用mongo 存进数据库
        #self.db.proxy.insert(data_list)


class ProxyServer:

    def __init__(self):
        self.p_getter = ProxyGetter()
        #新加----建立连接

    def __call__(self):
        self.p_getter.get_avtive_proxy()

    def refresh(self):
        mongo = MG()
        while mongo.db.proxy_new.find().count() <= 500:
            self.p_getter.get_avtive_proxy()


if __name__ == "__main__":

    ps = ProxyServer()
    ps()
    while True:
        ps.refresh()
