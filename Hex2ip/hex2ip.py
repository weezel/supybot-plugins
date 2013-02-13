#!/usr/bin/env python
# -*- coding: latin-1 -*-

import GeoIP

def hex2ip(host):
    """
    >>> hex2ip("5eed5ede@webchat.xs4all.nl")
    '94.237.94.222'
    >>> hex2ip("5eed5ede")
    '94.237.94.222'
    """
    conv = []
    splitidx = len(host)

    if len(host) != 8:
        splitidx = host.find("@")
        if splitidx == -1:
            return

    host = host[0:splitidx]

    for i in range(0, len(host) - 1):
        if i % 2 == 0:
            s = "%s%s" % (host[i], host[i + 1])
            conv.append(str(int(s, 16)))
    return ".".join(conv)

def getgeoip(ip):
    gi = GeoIP.open("/home/weezel/supybot/plugins/Hex2ip/GeoLiteCity.dat", GeoIP.GEOIP_STANDARD)
    r = gi.record_by_addr(ip)
    return "%s -> %s, %s" % (ip, r["city"], r["country_name"])

if __name__ == "__main__":
    ip = hex2ip("5eed5ede@webchat.xs4all.nl")
    print getgeoip(ip)
    #import doctest
    #doctest.testmod()

