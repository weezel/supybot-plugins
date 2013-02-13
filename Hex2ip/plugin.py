# -*- coding: latin-1 -*-

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import socket
import GeoIP

class Hex2ip(callbacks.Plugin):
    threaded = True
    def _hex2ip(self, host):
        ip = ""
        splitidx = len(host)

        if len(host) != 8:
            splitidx = host.find("@")
            if splitidx == -1:
                return

        host = host[0:splitidx]

        for i in range(0, len(host), 2):
            ip += "%d." % int(host[i : i + 2], 16)
        return ip.rstrip(".")

    def getgeoip(self, ip):
        gi = GeoIP.open("/home/weezel/supybot/plugins/Hex2ip/GeoLiteCity.dat", GeoIP.GEOIP_STANDARD)
        r = gi.record_by_addr(ip)
        return "%s, %s" % (r["city"], r["country_name"])

    def hex2ip(self, irc, msg, args):
        if len(args) < 1:
            irc.error("IP as a parameter, please")
            return
        try:
            hostmask = args[len(args) - 1].rstrip("\n")
            ip = self._hex2ip(hostmask)
            geoip = self.getgeoip(ip)
            fqdn = socket.getfqdn(ip)
            irc.reply("%s -> %s [%s]" % (ip, fqdn, geoip))
        except:
            irc.error("You fool!")
            return

Class = Hex2ip
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
