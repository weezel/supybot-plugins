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

BADURLS = re.compile("\.gif$|\.gz$|\.jpe?g$|\.png$|\.rar$|\.tar$|\.zip$|\.iso$|\.ogg$|\.mp[0-9]$|narf-archive\.com", re.IGNORECASE)
DB_URI= "/home/weezel/supybot/plugins/Youtube/linkstore.db"

class LinkDBApi:
    def __init__(self):
        self.testinit()

    def testinit(self):
        if not os.path.exists(DB_URI):
            try:
                F = open(DB_URI, "w")
                F.close()
            except IOError, ioe:
                callbacks.Plugin.log.debug("IOError in DB creation")
        else:
            return
        with sqlite.connect(DB_URI) as conn:
            q = u"CREATE TABLE links (last_access DATETIME NOT NULL, submitter TEXT, desc TEXT, link TEXT NOT NULL, PRIMARY KEY(link));"
            #conn.text_factory = str
            conn.text_factory = sqlite.OptimizedUnicode
            cur = conn.cursor()
            results = cur.execute(q)

    def __safe_unicode(self, s):
        """Return the unicode representation of obj"""
        try:
            return unicode(s, "utf-8")
        except UnicodeDecodeError:
            return unicode(s.decode("utf-8", "ignore"), "utf-8")
        except TypeError:
            return unicode(s)

    def insertLink(self, submitter, desc, link):
        """Insert a link into the DB"""
        if link == None or len(link) < len("http://"):
            return False
        desc = self.__safe_unicode(desc)
        link = self.__safe_unicode(link)

        with sqlite.connect(DB_URI) as conn:
            q = u"INSERT OR IGNORE INTO links VALUES (strftime('%s', 'now'), ?, ?, ?);"
            #conn.text_factory = str
            conn.text_factory = sqlite.OptimizedUnicode
            results = conn.execute(q, (submitter, desc, link))
        return True

    def isLinkOld(self, link):
        """Determine whether the link should be fetched again. """
        with sqlite.connect(DB_URI) as conn:
            q = u"SELECT * FROM links WHERE link LIKE ? AND (strftime('%s', 'now') - last_access) >= ?;"
            results = conn.execute(q, (link, 86400 * 7))
            results = results.fetchone()
        return True if results is not None else False

    def updateLinkLastseen(self, link):
        """docstring for updateLinkLastseen"""
        with sqlite.connect(DB_URI) as conn:
            q = u"UPDATE links SET last_access=strftime('%s', 'now') WHERE link LIKE ?;"
            results = conn.execute(q, [link])
        return True if results is not None else False

    def getByLink(self, link):
        """docstring for getLink"""
        link = self.__safe_unicode(link)
        with sqlite.connect(DB_URI) as conn:
            q = u"SELECT * FROM links WHERE link LIKE ?;"
            results = conn.execute(q, [link])
            results = results.fetchone()
        return "" if results is None else results

class Title(HTMLParser.HTMLParser):
    entitydefs = htmlentitydefs.entitydefs.copy()
    entitydefs['nbsp'] = ' '
    entitydefs['apos'] = '\''
    def __init__(self):
        self.inTitle = False
        self.title = ''
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.inTitle = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.inTitle = False

    def handle_data(self, data):
        if self.inTitle:
            self.title += data

    def handle_entityref(self, name):
        if self.inTitle:
            if name in self.entitydefs:
                self.title += self.entitydefs[name]

class Youtube(callbacks.Plugin):
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Youtube, self)
        self.__parent.__init__(irc)
        self.container = []

    def title(self, url):
        """<url> Returns the HTML <title>...</title> of a URL."""
        size = conf.supybot.protocols.http.peekSize()
        text = utils.web.getUrl(url, size=size)
        parser = Title()
        try:
            parser.feed(text)
        except HTMLParser.HTMLParseError:
            self.log.debug('Encountered a problem while parsing %u. Title might'
                           ' be already set', url)
        if parser.title:
            return utils.web.htmlToText(parser.title.strip())
        elif len(text) < size:
            return ''
        else:
            return ''

    def doPrivmsg(self, irc, msg):
        global BADURLS
        channel = msg.args[0]
        linkapi = LinkDBApi()

        if irc.isChannel(channel):
            if ircmsgs.isAction(msg):
                text = ircmsgs.unAction(msg)
            else:
                text = msg.args[1]

            for url in utils.web.urlRe.findall(text):
                if re.search(BADURLS, url) is not None:
                    continue

                url = unicode(url, "utf-8")
                urlseen = linkapi.getByLink(url)
                if urlseen is "":
                    titlename = self.title(url)
                    if len(titlename) > 0:
                        linkapi.insertLink(msg.nick, titlename, url)
                        try:
                            irc.reply("%s [%s]" % (titlename, url))
                        except UnicodeDecodeError:
                            irc.reply("%s [%s]" % (titlename.encode("utf-8"), url))
                else:
                    linkapi.updateLinkLastseen(url)
                    irc.reply("%s [%s]" % (urlseen[2], urlseen[3]))

Class = Youtube

