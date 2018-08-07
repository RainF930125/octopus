#!/usr/bin/python2.7

import os
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge

VIPS = os.getenv('MONITOR_VIPS', '').split(',')
GAUGE = Gauge('dup_vip_monitor', 'Duplication VIP monitor on VIP', ['vip'])
for vip in VIPS:
    GAUGE.labels(vip=vip)
DUP_BEFORE = 0

def app(environ, start_response):
    data = open('./dupvips.dat').read()
    new_dup = 1 if data else 0
    global VIPS, GAUGE, DUP_BEFORE
    if DUP_BEFORE:
        for vip in VIPS:
            GAUGE.labels(vip=vip).set(0)
    if new_dup:
        data = data.split(',')
        for d in data:
            GAUGE.labels(vip=d).set(1)
        DUP_BEFORE = 1
    data = generate_latest(GAUGE)
    start_response("200 OK", [
        ("Content-Type", CONTENT_TYPE_LATEST),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
