#!/usr/bin/python2.7

import jinja2
import netaddr
import os
import requests
import time


HOME = os.getenv('HOME')
HAPROXY_CONF = HOME + os.sep + 'haproxy.conf'
HAPROXY_PID = HOME + os.sep + 'haproxy.pid'
HAPROXY_TEMPLATE = HOME + os.sep + 'haproxy.template'


def get_sdn_info():
    endpoint = (
        'https://172.30.0.1:443/apis/network.openshift.io/v1/hostsubnets')
    token_file = '/var/run/secrets/kubernetes.io/serviceaccount/token'

    token = open(token_file).read().strip()
    headers = {"Authorization":"Bearer %s" % token}

    hostsubnets = requests.get(
        endpoint, headers=headers, verify=False).json()['items']
    sdn_info = [
        {'subnet': h['subnet'].replace('/', '-'),
         'host': h['host'],
         'sdnIP': str(netaddr.IPNetwork(h['subnet'])[1])}
        for h in hostsubnets]
    sdn_info.sort(key=lambda x: x['sdnIP'])
    return sdn_info


def try_refresh_haproxy_config():
    new_conf = jinja2.Template(open(HAPROXY_TEMPLATE).read()).render(
        sdn_info=get_sdn_info())
    old_conf = ''
    if os.path.exists(HAPROXY_CONF):
        old_conf = open(HAPROXY_CONF).read()
    if old_conf == new_conf:
        # No refresh is needed, so haproxy doesn't need reload
        return False
    else:
        # Config changed, haproxy need reload
        with open(HAPROXY_CONF, 'w+') as f:
            f.write(new_conf)
        return True


def pid_running(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    else:
        return True


def manage_haproxy():
    reload_haproxy = try_refresh_haproxy_config()
    pid = ''
    if os.path.exists(HAPROXY_PID):
        pid = open(HAPROXY_PID).read().strip()
    if reload_haproxy or not pid or not pid_running(pid):
        sf_opt = ("-sf %s" % pid) if pid else ""
        os.system('haproxy -f %s -p %s %s' % (
            HAPROXY_CONF, HAPROXY_PID, sf_opt))


if __name__=='__main__':
    while True:
        manage_haproxy()
        time.sleep(os.getenv('NODES_FETCH_INTV', 300))
