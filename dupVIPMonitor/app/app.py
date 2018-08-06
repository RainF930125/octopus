#!/usr/bin/python2.7

import os
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge

vips = os.getenv('MONITOR_VIPS', '').split(',')
GAUGES = {
    vip: Gauge(('dup_vip_monitor_on_%s' % vip).replace('.', '_'),
               ('Duplication VIP monitor on VIP %s' % vip).replace('.', '_'))
    for vip in vips}
dup_before = 0

def app(environ, start_response):
    data = open('./dupvips.dat').read()
    new_dup = 1 if data else 0
    global GAUGEa, dup_before
    if dup_before:
        for g in GAUGES.itervalues():
            g.set(0)
    if new_dup:
        data = data.split(',')
        for d in data:
            GAUGES[d].set(1)
        dup_before = 1
    data = [generate_latest(g) for g in GAUGES.values()]
    data_len = len(''.join(data))
    start_response("200 OK", [
        ("Content-Type", CONTENT_TYPE_LATEST),
        ("Content-Length", str(data_len))
    ])
    return iter(data)
