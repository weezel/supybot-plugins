# -*- coding: utf-8 -*-
###
# Copyright (c) 2015, Ville Valkonen
# All rights reserved.
###

import sys

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import re
import requests
import sqlite3 as sqlite
import time

badurls = re.compile("\.gif$|\.gz$|\.jpe?g$|\.png$|\.rar$|\.tar$|\.zip$|" + \
                     "\.iso$|\.ogg$|\.mp[0-9]$|narf-archive\.com", \
                     re.IGNORECASE)
dbfile = "/home/weezel/supybot/plugins/Youtube/linkstore.db"
dbschema = "/home/weezel/supybot/plugins/Youtube/linkstore.sql"
certfile = "/etc/ssl/cert.pem"


def safe_unicode(s):
    """Return the unicode representation of obj"""
    try:
        result = unicode(s, "utf-8").decode("utf-8")
    except UnicodeDecodeError:
        result = s.decode("latin-1")
    except TypeError:
        result = unicode(s)
    return result

class LinkDBApi(object):
    def __init__(self):
        self.__testinit()
        self.conn = None
        self.cur = None

    def __testinit(self):
        # TODO check if database exists
        self.conn = sqlite.connect(dbfile)
        self.cur = self.conn.cursor()

        with open(dbschema, "r") as f:
            sql = f.read()
            self.cur.executescript(sql)
        self.cur.close()
        self.conn.close()

    def insert_and_get_uid(self, username):
        """
        Try to insert username in to database and if exists, ignore.
        Return uid of given username.
        """
        uid = -1

        with sqlite.connect(dbfile) as conn:
            cur = conn.cursor()
            q1 = safe_unicode(u"INSERT OR IGNORE INTO user VALUES (null, ?);")
            cur.execute(q1, [username])
            conn.commit()

            q2 = safe_unicode(u"SELECT uid FROM user WHERE name = ?;")
            res = cur.execute(q2, [username])
            uid = res.fetchone()[0]
        return uid

    def get_link_by_lid(self, lid):
        """
        Return [link, title]
        """
        item = None

        with sqlite.connect(dbfile) as conn:
            cur = conn.cursor()
            q = safe_unicode(u"SELECT link, title FROM link " \
                            + "WHERE l.lid = ?;")
            res = cur.execute(q, [lid])
            item = res.fetchone()
        return item

    def get_url_and_timestamp(self, link):
        with sqlite.connect(dbfile) as conn:
            q = safe_unicode(u"SELECT title, last_access FROM link WHERE link = ?;")
            res = conn.execute(q, [link])
            results = res.fetchone()
        return "" if results is None else results

    def insert_and_get_linkid(self, uid, title, link):
        """
        Try to instert link into the link table, if link exists, ignore.
        Finally return link id.
        """
        linkid = -1

        with sqlite.connect(dbfile) as conn:
            cur = conn.cursor()
            q1 = safe_unicode(u"INSERT OR IGNORE INTO link " \
                             + "VALUES (null, strftime('%s', 'now'), " \
                             + "?, ?, ?);")
            cur.execute(q1, (uid, title, link))
            conn.commit()

            q2 = safe_unicode(u"SELECT lid FROM link WHERE link = ?;")
            res = cur.execute(q2, [link])
            linkid = res.fetchone()[0]
        return linkid

    def is_link_old(self, link):
        """Determine whether the link should be fetched again."""
        with sqlite.connect(dbfile) as conn:
            q = safe_unicode(u"SELECT * FROM link WHERE link = ? " \
                            + "AND (strftime('%s', 'now') - last_access) >= ?;")
            results = conn.execute(q, (link, 86400 * 7))
            results = results.fetchone()
        return True if results is not None else False

    def updateLinkLastseen(self, link):
        """docstring for updateLinkLastseen"""
        with sqlite.connect(dbfile) as conn:
            q = safe_unicode(u"UPDATE link SET " \
                    + "last_access=strftime('%s', 'now') WHERE link = ?;")
            results = conn.execute(q, [link])

def get_url_title(url):
    read = unicode()
    e = unicode()
    max_size = 262144 # 0.25 MB

    try:
        # TODO SSL doesn't work yet
        resp = requests.get(url, timeout=5, stream=True, verify=False)
    except requests.exceptions.MissingSchema:
        return unicode()

    for n in resp.iter_content(2048):
        read += safe_unicode(n)
        e = read.find(u"</title>")

        if e > 0:
            break
        if len(read) > max_size:
            break

    resp.close()

    b = read.find(u"<title>")
    if b > 0:
        b += 7
    else:
        return unicode() # no <title> found

    return read[b:e]

if __name__ == '__main__':
    print get_url_title("hasdofijasdf")
    print get_url_title("http://severi.lan")
    print get_url_title("http://severi.lan/weezel/pics")
    print get_url_title("https://severi.lan")
    print get_url_title("https://severi.lan/weezel/pics")
    sys.exit(0)

class Youtube(callbacks.Plugin):
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Youtube, self)
        self.__parent.__init__(irc)
        self.db = LinkDBApi()

    def doPrivmsg(self, irc, msg):
        channel = msg.args[0]
        linkapi = LinkDBApi()

        if irc.isChannel(channel):
            if ircmsgs.isAction(msg):
                text = ircmsgs.unAction(msg)
            else:
                text = msg.args[1]

            usrmsg = safe_unicode(text)
            for url in utils.web.urlRe.findall(usrmsg):
                if re.search(badurls, url) is not None:
                    continue

                uid = linkapi.insert_and_get_uid(msg.nick)
                urlseen = linkapi.get_url_and_timestamp(url)

                if urlseen is "":
                    titlename = get_url_title(url)
                    if len(titlename) > 0:
                        linkid = linkapi.insert_and_get_linkid(uid, titlename, url)
                        irc.reply("%s" % (titlename))
                else:
                    if linkapi.is_link_old(url):
                        linkapi.updateLinkLastseen(url)
                    irc.reply("%s [title updated: %s]" % (urlseen[0], time.ctime(urlseen[1])))

Class = Youtube

