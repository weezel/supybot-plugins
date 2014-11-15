# -*- coding: utf-8 -*-
###
# Copyright (c) 2008-2012, Ville Valkonen
# All rights reserved.
#
#
###

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import supybot.utils.web as web
import sqlite3 as sqlite
import HTMLParser
import htmlentitydefs
import os
import re


DB_URI = "/home/weezel/supybot/plugins/Glitter/glitter.db"

class GlitterDB:
    def __init__(self):
        self.testinit()

    def testinit(self):
        if not os.path.exists(DB_URI):
            try:
                F = open(DB_URI, "r")
                F.close()
            except IOError, ioe:
                callback.Plugin.log.debug("IOError in DB creation")
        else:
            return # XXX Remove this to proceed..

        # TODO Generate database if it doesn't exist
        #with sqlite.connect(DB_URI) as conn:
        #    q = u""
        #    conn.text_factory = sqlite.OptimizedUnicode
        #    cur = conn.cursor()
        #    results = cur.execute(q)

    def __safe_unicode(self, s):
        """Return the unicode representation of obj"""
        return unicode(s, "utf-8").decode("utf-8")
        #try:
        #    return unicode(s, "utf-8")
        #except UnicodeDecodeError:
        #    return unicode(s.decode("utf-8", "ignore"), "utf-8")
        #except TypeError:
        #    return unicode(s)

    def insertNick(self, nick):
        unick = self.__safe_unicode(nick)
        with sqlite.connect(DB_URI) as conn:
            q = self.__safe_unicode("INSERT INTO nick VALUES (null, ?);")
            conn.text_factory = sqlite.OptimizedUnicode
            conn.execute(q, [unick])

    def getNick(self, nick):
        unick = self.__safe_unicode(nick)
        with sqlite.connect(DB_URI) as conn:
            q = self.__safe_unicode("SELECT nid FROM nick WHERE nick.nick LIKE ?;")
            conn.text_factory = sqlite.OptimizedUnicode
            results = conn.execute(q, [unick])
            return results.fetchone()[0]
        return ""

    def insertChannel(self, chan):
        uchan = self.__safe_unicode(chan)
        with sqlite.connect(DB_URI) as conn:
            q = self.__safe_unicode("INSERT INTO channel VALUES (null, ?);")
            conn.text_factory = sqlite.OptimizedUnicode
            conn.execute(q, [uchan])

    def getChannel(self, chan):
        uchan = self.__safe_unicode(chan)
        with sqlite.connect(DB_URI) as conn:
            q = self.__safe_unicode("SELECT cid FROM channel WHERE channel.channel LIKE ?;")
            conn.text_factory = sqlite.OptimizedUnicode
            results = conn.execute(q, [uchan])
            return results.fetchone()[0]
        return ""

    def insertMessage(self, msg):
        umsg = self.__safe_unicode(msg)
        with sqlite.connect(DB_URI) as conn:
            q = self.__safe_unicode("INSERT INTO message VALUES (null, ?);")
            conn.text_factory = sqlite.OptimizedUnicode
            conn.execute(q, [umsg])

    def getMessage(self, msg):
        umsg = self.__safe_unicode(msg)
        with sqlite.connect(DB_URI) as conn:
            q = self.__safe_unicode("SELECT mid FROM message WHERE message.message LIKE ?;")
            conn.text_factory = sqlite.OptimizedUnicode
            results = conn.execute(q, [umsg])
            return results.fetchone()[0]
        return ""

    def insertTags(self, tags, mid):
        utags = [(mid, self.__safe_unicode(tag),) for tag in tags]
        with sqlite.connect(DB_URI) as conn:
            q = self.__safe_unicode("INSERT OR IGNORE INTO tag VALUES (null, ?, ?);")
            conn.text_factory = sqlite.OptimizedUnicode
            conn.executemany(q, utags)

    def getTags(self, tags):
        #utags = [self.__safe_unicode(tag) for tag in tags]
        utags = map(self.__safe_unicode, tags)
        foundtags = list()

        for tag in utags:
            with sqlite.connect(DB_URI) as conn:
                q = self.__safe_unicode("SELECT tid FROM tag WHERE tag.tag LIKE ?;")
                conn.text_factory = sqlite.OptimizedUnicode
                results = conn.execute(q, [tag])
                foundtags.append(results.fetchall()[0])
        return foundtags

    def insertGlitter(self, pnid, pcid, pmid, ptids):
        for tid in ptids:
            with sqlite.connect(DB_URI) as conn:
                q = self.__safe_unicode("INSERT INTO glitter VALUES " + \
                              "(null, strftime('%s', 'now'), " + \
                              "?, ?, ?, ?);")
                conn.text_factory = sqlite.OptimizedUnicode
                results = conn.execute(q, (pnid, pcid, pmid, tid[0]))


class Glitter(callbacks.Plugin):
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Glitter, self)
        self.__parent.__init__(irc)

    def doPrivmsg(self, irc, msg):
        channel = msg.args[0]
        nick = msg.nick
        nid = cid = mid = tid = 0
        p = re.compile("#[a-zA-Z0-9_-]+")
        db = None

        if irc.isChannel(channel):
            if ircmsgs.isAction(msg):
                message = ircmsgs.unAction(msg)
            else:
                message = msg.args[1]

            tags = re.findall(p, message)
            if len(tags) > 0:
                db = GlitterDB()

                try:
                    db.insertNick(nick)
                except sqlite.IntegrityError, ie:
                    self.log.debug("Inserting '%s, %s, %s, %s' failed." \
                            % (nick, channel, message, tags))
                nid = db.getNick(nick)

                try:
                    db.insertChannel(channel)
                except sqlite.IntegrityError, ie:
                    self.log.debug("Inserting '%s, %s, %s, %s' failed." \
                            % (nick, channel, message, tags))
                cid = db.getChannel(channel)

                try:
                    db.insertMessage(message)
                except sqlite.IntegrityError, ie:
                    self.log.debug("Inserting '%s, %s, %s, %s' failed." \
                            % (nick, channel, message, tags))
                mid = db.getMessage(message)

                try:
                    db.insertTags(tags, mid)
                except sqlite.IntegrityError, ie:
                    self.log.debug("Inserting '%s, %s, %s, %s' failed." \
                            % (nick, channel, message, tags))
                tid = db.getTags(tags)

                try:
                    db.insertGlitter(nid, cid, mid, tid)
                except sqlite.IntegrityError, ie:
                    self.log.debug("Inserting '%s, %s, %s, %s' failed." \
                            % (nick, channel, message, tags))
Class = Glitter

