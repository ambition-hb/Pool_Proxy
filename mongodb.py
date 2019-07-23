#coding:utf8
from pymongo import MongoClient

class MG:
    def __init__(self):
        #建立连接
        uri = 'mongodb://spider:123456@192.168.3.138:20250'
        self.client = MongoClient(uri)
        # self.client = MongoClient("localhost", 27017)
        self.db = self.client.zhihu