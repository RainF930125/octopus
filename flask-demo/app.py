from flask import Flask
from flask import request
import os
import time


application = Flask(__name__)
READY_COUNT = 0
HALFREADY_COUNT = 0
ALIVE_COUNT = 0


@application.route("/")
def hello():
    return "Hello World!"


@application.route("/ready")
def ready():
    global READY_COUNT
    if READY_COUNT <= 2:
        time.sleep(5)
        READY_COUNT += 1
    return "Ready!", 200


@application.route("/halfready")
def halfready():
    global HALFREADY_COUNT
    HALFREADY_COUNT += 1
    if (HALFREADY_COUNT / 5) % 2 != 0:
        return "Ready!"
    return "Not ready", 503


@application.route("/alive")
def alive():
    global ALIVE_COUNT
    ALIVE_COUNT += 1
    if (ALIVE_COUNT / 5) % 2 == 0:
        return "I'm alive!"
    return "Not alive", 503


@application.route("/headers")
def headers():
    return 'Request headers for %s are: %r' % (request.url, request.headers)


@application.route("/hdrs")
def hdrs():
    print 'Request headers for %s are: %r' % (request.url, request.headers)
    return 'ok'


@application.route("/clientip")
def clientip():
    return 'Hi, %r, this is %s' % (
        request.headers.get('X-Forwarded-For'),
        os.popen('hostname -i').read())


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080)
