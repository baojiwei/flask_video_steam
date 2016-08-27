#!/usr/bin/env python
# encoding: utf-8

from time import time
import redis
from datetime import datetime

cache_db = redis.StrictRedis()
class Camera(object):
    def __init__(self,name='default_camera'):
        self.name = name

    def get_frame(self):
        return self.frames[int(time()*2) %3 ]

    def save_frame(self,content,numbers=10):
        #key:value储存时间为hmtable中的长度的100倍
        timeout = numbers*100
        curimage_key = str(datetime.now)
        cache_db.setex(curimage_key,content,timeout)

        #生成序列组
        #每次丢掉第一帧
        image_indexs = range(0,numbers)
        image_keys = cache_db.hmget(self.name,image_indexs)
        image_keys = image_keys[1:]
        image_keys.append(curimage_key)

        #更新
        vals = {}
        for i in image_indexs:
            vals.update({i:image_keys[i]})
        cache_db.hmset(self.name,vals)
        #返回当前的key
        return curimage_key
