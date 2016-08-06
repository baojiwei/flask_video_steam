#!/usr/bin/env python
# encoding: utf-8

from time import time
import redis

cache_db = redis.StrictRedis()
class Camera(object):
    def __init__(self):
        pass

    def get_frame(self):
        return self.frames[int(time()*2) %3 ]
