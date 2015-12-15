###
# Copyright (c) 2015, Ville Valkonen
# All rights reserved.
###

import lxml.html
import requests

import re

class TvOhjelmat(object):
    def __init__(self):
        self.url = "http://www.tv-ohjelmat.com/"
        self.parsed_data = None
        self.chanmapping = { "tv1_" : "TV1",        \
                             "tv2_" : "TV2",        \
                             "mtv_" : "MTV3",       \
                             "nel_" : "Nelonen",    \
                             "tvt_" : "SubTV",      \
                             "nep_" : "JIM",        \
                             "tvt_" : "SubTV",      \
                             "yte_" : "Yle Teema",  \
                             "tvt_" : "SubTV",      \
                             "fsd_" : "Yle Fem",    \
                             "tv5_" : "TV5",        \
                             "voi_" : "6",          \
                             "liv_" : "Liv",        \
                             "ava_" : "Ava" }

    def __fetch(self):
        return requests.get(self.url)

    def parseAndFetch(self):
        tmp = self.__fetch()
        self.parsed_data = lxml.html.fromstring(tmp.content)

    def iteratorOnAir(self):
        for tag in self.parsed_data.xpath('//p[contains(@class, ' + \
                                          '"is_on_air")]'):
            yield tag

    def parseChannel(self, tag):
        if not isinstance(tag, lxml.html.HtmlElement):
            return u""
        for chan in self.chanmapping.iterkeys():
            if tag.get("id").startswith(chan):
                return self.chanmapping[chan]
        return u""

    def parseStartTime(self, tag):
        if not isinstance(tag, lxml.html.HtmlElement):
            return u""
        return " ".join(tag.xpath('./b/text()')).replace(".", ":")

    def parseProgram(self, tag):
        if not isinstance(tag, lxml.html.HtmlElement):
            return u""
        prog = " ".join(tag.xpath('./text()'))
        prog = re.sub("\s", " ", prog)
        return prog.strip("\n").lstrip(" ").rstrip(" ")

if __name__ == '__main__':
    import sys

    tv = TvOhjelmat()

    tv.parseAndFetch()

    for prog in tv.iteratorOnAir():
        print "[%-7s] %5s: %s" % (tv.parseChannel(prog),   \
                               tv.parseStartTime(prog), \
                               tv.parseProgram(prog))

    sys.exit(0)

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Tv(callbacks.Plugin):

    def tv(self, irc, msg, args):
        threaded = True
        tv = TvOhjelmat()
        onair = u""

        tv.parseAndFetch()

        for prog in tv.iteratorOnAir():
            channel = tv.parseChannel(prog)
            stime = tv.parseStartTime(prog)
            prog = tv.parseProgram(prog)
            onair += "[%s] %s: %s, " % (channel, ircutils.bold(stime), prog)
        irc.reply(onair.rstrip(", "))

Class = Tv

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
