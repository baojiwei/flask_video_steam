#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, render_template, Response, request
from camera import Camera
import redis
from cStringIO import StringIO
from datetime import datetime

app = Flask(__name__)

cache_db = redis.StrictRedis()

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_push', methods=['POST'])
def video_push_cache():
    '''推流'''
    file = request.files('uploaded_file')
    timeout = 10
    content = StringIO(file.read())

    #先把图像数据放入到setex中
        #先以时间戳生成key
    curimage_key = str(datetime.now)
    cache_db.setex(curimage_key,content,timeout)

    #生成序列组
    image_indexs = range(1,11)
    image_keys = cache_db.hmget('images',image_indexs)
    image_keys = image_keys[1:]
    image_keys.append(curimage_key)

    #更新
    vals = {}
    for i in image_indexs:
        vals.update({i:image_keys[i]})
    cache_db.hmset('images',vals)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threader=True)
