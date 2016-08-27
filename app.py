#!/usr/bin/env python
# encoding: utf-8

from flask import Flask, render_template, Response, request, session
from camera import Camera
import redis
import os
from cStringIO import StringIO

app = Flask(__name__)

cache_db = redis.StrictRedis()
camera = Camera()
local_access = {}

@app.route('/')
def index():
    return render_template('index.html')

def gen(listener):
    #flag = True
    #while flag:
    #    frame,flag = camera.get_frame(acess_key)
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + listener.next() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    if not session['session_id']:
        access_key = session['session_id'] = os.urandom(24)
    else:
        access_key = session['session_id']

    if local_access.has_key(access_key):
        local_access[access_key].close()
    local_access[access_key] = cache_db.pubsub()
    local_access[access_key].subscribe(camera.name)

    return Response(gen(local_access[access_key]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_push', methods=['POST'])
def video_push_cache():
    '''推流'''
    file = request.files('uploaded_file')
    content = StringIO(file.read())

    curimage_key = camera.save_frame(content)
    cache_db.publish(camera.name, curimage_key)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threader=True)
