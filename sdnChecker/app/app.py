#!/usr/bin/python2.7

import netaddr
import os
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge
import requests


MY_IP = netaddr.IPAddress(os.popen('hostname -i').read().strip())
NAMESPACE = os.getenv('NAMESPACE')
STAT_MY = 'X'
STAT_PEER_PASS = '1'
STAT_PEER_FAIL = '0'
GAUGE = Gauge(
    'sdn_connectivity', 'SDN connectivity checking between nodes',
    ['peer_left', 'peer_right'])
LABEL_FMT = 'sdn_check_between_%s_AND_%s'


def get_single_stat():
    endpoint = 'http://localhost:1936/haproxy?stats;csv'
    # echo -n 'admin:password' | base64
    token = 'YWRtaW46cGFzc3dvcmQ='
    headers = {"Authorization":"Basic %s" % token}

    stats_info = requests.get(
        endpoint, headers=headers).text.strip().split('\n')[4:-1]
    serial = ''
    hosts = []
    for info in stats_info:
        item = info.split(',')
        host, ip, prefix = item[1].rsplit('-', 2)
        hosts.append(host)
        stat = item[36]
        cidr = ip + '/' + prefix
        if MY_IP in netaddr.IPNetwork(cidr):
            serial += STAT_MY
        elif stat == 'L4TOUT':
            serial += STAT_PEER_FAIL
        else:
            serial += STAT_PEER_PASS
    serial = str(','.join(hosts)) + '\n' + serial
    # text is enough
    return serial


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
    hosts, mystat = get_single_stat().split('\n')

    num_stats = len(mystat)
    if num_stats != len(all_pod_ips):
        return "Some error we cannot handle happened", 500

    all_stats = []
    failed_peers = []
    for i in range(num_stats):
        peer_stat = mystat[i]
        if peer_stat == STAT_MY:
            stat = mystat
        elif peer_stat == STAT_PEER_PASS:
            peer_ip = all_pod_ips[i]
            stat = requests.get('http://%s:8080/single' % peer_ip).text.strip(
                ).split('\n')[1]
        else:
            stat = '0' * i + 'X' + '0' * (num_stats -1 -i)
            failed_peers.append(i)
        all_stats.append(stat)
    for i in failed_peers:
        all_stats[i] = ''.join([stat[i] for stat in all_stats])
    return str(hosts + '\n' + '\n'.join(all_stats))


def app(environ, start_response):
    if environ.get('PATH_INFO', '/') == '/single':
        data = get_single_stat()
    elif environ.get('PATH_INFO', '/') == '/raw':
        data = get_stats()
    else:
        hosts, stats = get_stats().split('\n', 1)
        hosts = hosts.split(',')
        stats = stats.split('\n')
        num_stats = len(stats)
        global GAUGE
        for i in range(num_stats):
            for j in range(i + 1, num_stats):
                GAUGE.labels(peer_left=hosts[i], peer_right=hosts[j]).set(
                    stats[i][j])
        data = generate_latest(GAUGE)
    start_response("200 OK", [
        ("Content-Type", CONTENT_TYPE_LATEST),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
