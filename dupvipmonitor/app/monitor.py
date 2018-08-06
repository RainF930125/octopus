#!/usr/bin/python2.7

import commands
import os
import time


def monitor(vips, intv):
    dupvips = []
    for vip in vips:
        status, _ = commands.getstatusoutput('./arping2 %s -d -c3 -w%s' % (
            vip, intv))
        if status != 0:
            dupvips.append(vip)
    with open('./dupvips.dat', 'w+') as f:
        f.write(','.join(dupvips))


if __name__ == '__main__':
    vips = os.getenv('MONITOR_VIPS', '').split(',')
    if not vips[0]:
        os.exit(1)
    arping_intv = int(os.getenv('ARPING_INTERVAL', 0.2) * 1000000)
    intv = int(os.getenv('MONITOR_INTERVAL', 6))
    while True:
        monitor(vips, arping_intv)
        time.sleep(intv)
