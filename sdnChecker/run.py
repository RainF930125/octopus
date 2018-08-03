#!/usr/bin/python2.7

from flask import Flask
import netaddr
import os
import requests


application = Flask(__name__)
myIP = netaddr.IPAddress(os.popen('hostname -i').read().strip())

@application.route("/")
def get_stats():
    endpoint = 'http://localhost:1936/haproxy?stats;csv'
    # echo -n 'admin:password' | base64
    token = 'YWRtaW46cGFzc3dvcmQ='
    headers = {"Authorization":"Basic %s" % token}

    stats_info = requests.get(
        endpoint, headers=headers).text.strip().split('\n')[4:-1]
    serial = ''
    for info in stats_info:
        item = info.split(',')
        cidr = item[1]
        stat = item[36]
        cidr = cidr.replace('-', '/')
        if myIP in netaddr.IPNetwork(cidr):
            serial += 'X'
        elif stat == 'L4TOUT':
            serial += '0'
        else:
            serial += '1'
    return serial, 200


if __name__ == "__main__":
    os.system('python haproxy_manager.py &')
    application.run(host='0.0.0.0', port=8080)
