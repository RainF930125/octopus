#!/usr/bin/python2.7

from flask import Flask
import netaddr
import os
import requests


application = Flask(__name__)
MY_IP = netaddr.IPAddress(os.popen('hostname -i').read().strip())
NAMESPACE = os.getenv('NAMESPACE')
STAT_MY = 'X'
STAT_PEER_PASS = '1'
STAT_PEER_FAIL = '0'


@application.route("/single")
def get_single_stat():
    print "get_single_stat"
    endpoint = 'http://localhost:1936/haproxy?stats;csv'
    # echo -n 'admin:password' | base64
    token = 'YWRtaW46cGFzc3dvcmQ='
    headers = {"Authorization":"Basic %s" % token}

    stats_info = requests.get(
        endpoint, headers=headers).text.strip().split('\n')[4:-1]
    print "Raw stats_info is:", stats_info
    serial = ''
    for info in stats_info:
        item = info.split(',')
        cidr = item[1]
        stat = item[36]
        cidr = cidr.replace('-', '/')
        if MY_IP in netaddr.IPNetwork(cidr):
            serial += STAT_MY
        elif stat == 'L4TOUT':
            serial += STAT_PEER_FAIL
        else:
            serial += STAT_PEER_PASS
    # text is enough
    return serial, 200


@application.route("/")
def get_stats():
    def get_peers():
        endpoint = ('https://172.30.0.1:443/api/v1/namespaces/%s/pods?'
                    'labelSelector=name=sdnchecker') % NAMESPACE
        token_file = '/var/run/secrets/kubernetes.io/serviceaccount/token'
        token = open(token_file).read().strip()
        headers = {"Authorization":"Bearer %s" % token}
        all_pod_ips = [
            pod['status']['podIP']
            for pod in requests.get(
                endpoint, headers=headers, verify=False).json()['items']]
        all_pod_ips.sort()
        return all_pod_ips

    all_pod_ips = get_peers()
    mystat, _ = get_single_stat()
    num_stats = len(mystat)
    if num_stats != len(all_pod_ips):
        return "Some error we cannot handle happened", 500

    all_stats = []
    for i in range(len(mystat)):
        peer_stat = mystat[i]
        if peer_stat == STAT_MY:
            stat = mystat
        elif peer_stat == STAT_PEER_PASS:
            peer_ip = all_pod_ips[i]
            stat = requests.get('http://%s:8080/single' % peer_ip).text.strip()
        else:
            stat = '0' * i + 'X' + '0' * (num_stats -1 -i)
        all_stats.append(stat)
    return '\n'.join(all_stats), 200
