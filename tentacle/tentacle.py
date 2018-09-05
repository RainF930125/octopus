#!/usr/bin/python2.7

import ast
from flask import Flask
from flask import request
import os
import requests
import ruamel.yaml as yaml


app = Flask(__name__)


@app.route('/nodemap', methods=['POST'])
def update_nodemap():
    """ You should use this API to registry masters and nodes first, e.g.:
            curl -X POST http://0.0.0.0:9696/nodemap -d \
            '{"master": ["master1"], "node": ["node1","node2","node3"]}'
        If a master also have compute role, you can put it into node list.
    """

    with open('/var/lib/tentacle.dat', 'w+') as f:
        f.write(request.data)
    return 'Nodes map updated'


def process_members(method, data, role):
    if not os.path.exists('/var/lib/tentacle.dat'):
        return 'Not nodemap post yet', 404

    nodemap = ast.literal_eval(open('/var/lib/tentacle.dat').read())
    if method == 'POST':
        for member in nodemap[role]:
            endpoint = 'http://%(host)s:9696/%(role)s/%(host)s' % {
                'host': member, 'role': role}
            info = requests.post(endpoint, json=data)
        return "Masters/Nodes set done\n"
    else:
        all_info = {}
        for member in nodemap[role]:
            endpoint = 'http://%(host)s:9696/%(role)s/%(host)s' % {
                'host': member, 'role': role}
            info = requests.get(endpoint).text.strip()
            all_info[member] = ast.literal_eval(info)
        return str(all_info)


@app.route('/masters', methods=['POST', 'GET'])
def process_masters():
    """ This API helps to get or set all masters config. """

    method = request.method
    data = ''
    if method == 'POST':
        data = ast.literal_eval(request.data)
    return process_members(method, data, "master")


@app.route('/nodes', methods=['POST', 'GET'])
def process_nodes():
    """ This API helps to get or set all nodes config. """

    method = request.method
    data = ''
    if method == 'POST':
        data = ast.literal_eval(request.data)
    return process_members(method, data, "node")


def process_host(host, method, data, role):
    def get_confs(conf):
        ret = {}
        if conf and os.path.exists(conf):
            with open(conf) as f:
                ret = yaml.load(f, yaml.RoundTripLoader, preserve_quotes=True)
        return ret

    def set_confs(conf, data):
        with open(conf, 'w+') as f:
            yaml.dump(data, f, Dumper=yaml.RoundTripDumper)

    def get_conf_file(role):
        return {
            'node': '/etc/origin/node/node-config.yaml',
            'master': '/etc/origin/master/master-config.yaml'}.get(role, '')

    hostname = os.uname()[1]
    if host == hostname:
        conf_file = get_conf_file(role)
        confs = get_confs(conf_file)
        if not confs:
            return 'Target config file not exists', 404

        if method == 'POST':
            if role == 'master':
                configuration = {}
                for k in data:
                    if k in ('cpuRequestToLimitPercent',
                             'memoryRequestToLimitPercent'):
                        configration[k] = data[k]
                if configuration:
                    configuration['apiVersion'] = 'v1'
                    confs['admissionConfig']['pluginConfig'].update(
                        {'ClusterResourceOverride': configuration})
                if 'subdomain' in data:
                    confs['routingConfig']['subdomain'] = data['subdomain']
                set_confs(conf_file, confs)
                os.system(
                    'nohup systemctl restart origin-master-api '
                    'origin-master-controllers &')
                return 'Set master done'
            else:
                for k in data:
                    if k in ('max-pods', 'kube-reserved', 'system-reserved'):
                        confs['kubeletArguments'][k] = data[k]
                set_confs(conf_file, confs)
                os.system('nohup systemctl restart origin-node &')
                return 'Set node done'
        else:
            if role == 'master':
                d = {
                    k: confs['admissionConfig']['pluginConfig'].get(
                        'ClusterResourceOverride', {}).get(
                        'configuration', {}).get(k)
                    for k in ('cpuRequestToLimitPercent',
                              'memoryRequestToLimitPercent')}
                d['subdomain'] = confs['routingConfig']['subdomain']
                d = str(d)
            else:
                d = str({
                    k: confs['kubeletArguments'].get(k)
                    for k in ('kube-reserved', 'system-reserved', 'max-pods')})
            return d
    else:
        # we will work as proxy for request to target host
        if method == 'POST':
            endpoint = 'http://%(host)s:9696/%(role)s/%(host)s' % {
                'host': host, 'role': role}
            info = requests.post(endpoint, json=data)
            return "Node set done"
        else:
            endpoint = 'http://%(host)s:9696/%(role)s/%(host)s' % {
                'host': host, 'role': role}
            info = requests.get(endpoint).text.strip()
            return info


@app.route('/master/<host>', methods=['GET', 'POST'])
def process_master(host):
    method = request.method
    data = ''
    if method == 'POST':
        data = ast.literal_eval(request.data)
    return process_host(host, method, data, "master")


@app.route('/node/<host>', methods=['GET', 'POST'])
def process_node(host):
    method = request.method
    data = ''
    if method == 'POST':
        data = ast.literal_eval(request.data)
    return process_host(host, method, data, "node")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9696)
