# -*- coding: utf-8 -*-
###
# Copyright (c) 2015, Ville Valkonen
# All rights reserved.
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import sys

from os.path import isfile
import queryeng as qe

db = qe.DBSearch()

def safe_unicode(s):
    """Return the unicode representation of obj"""
    try:
        return unicode(s, "utf-8").decode("utf-8")
    except UnicodeDecodeError, ude:
        return s.decode("latin-1")

class Sivsan(callbacks.Plugin):
    Threaded = True

    def sivsan(self, irc, msg, args):
        results = list()

        if len(args) < 1:
            irc.error("usage: @sivsan [--descincludes] [searchterm | " + \
                    "*searchterm* | searchterm* | *searchterm]")
            return

        elif len(args) == 1:
            query = safe_unicode(args[0])
            if "*" in args[0]:
                if args[0][0] == '*' and args[0][len(args[0]) - 1] == '*':
                    results = db.wordincludes(query.replace('*', ''))
                elif args[0][0] == '*':
                    results = db.wordendswith(query.replace('*', ''))
                elif args[0][len(args[0]) - 1] == '*':
                    results = db.wordstartswith(query.replace('*', ''))
            else:
                results = db.wordequals(query)
        elif len(args) == 2:
            query = safe_unicode(args[1])
            if "--descincludes" in args[0]:
                results = db.descincludes(query.replace('*', ''))

        # Time to let user know the results
        if len(results) == 1:
            results = results[0]
            irc.reply(u"%s = %s" % (results[0], results[1]))
        else:
            words = [i[0] for i in results]
            irc.reply(u"Found: %s" % (", ".join(words)))

Class = Sivsan
