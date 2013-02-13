#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sqlite3 as sqlite
import os

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
                print "Kääk"
                os.exit(1)
        else:
            return
        with sqlite.connect(DB_URI) as conn:
            q = u"CREATE TABLE links (last_access DATETIME NOT NULL, submitter TEXT, desc TEXT, link TEXT NOT NULL, PRIMARY KEY(link));"
            cur = conn.cursor()
            results = cur.execute(q)

    def __insertLink(self, submitter, desc, link):
        """docstring for insertLink"""
        if link == None or len(link) < len("http://"):
            return False
        with sqlite.connect(DB_URI) as conn:
            q = u"INSERT OR IGNORE INTO links VALUES (strftime('%s', 'now'), ?, ?, ?);"
            results = conn.execute(q, (submitter, desc, link))
        return True

    def __isLinkOld(self, link):
        """Determine whether the link should be fetched again. """
        with sqlite.connect(DB_URI) as conn:
            q = u"SELECT * FROM links WHERE link LIKE ? AND (strftime('%s', 'now') - last_access) >= ?;"
            results = conn.execute(q, (link, 86400))
            results = results.fetchone()
        return True if results is not None else False

    def __updateLinkLastseen(self, link):
        """docstring for updateLinkData"""
        with sqlite.connect(DB_URI) as conn:
            q = u"UPDATE links SET last_access=strftime('%s', 'now') WHERE link LIKE ?;"
            results = conn.execute(q, [link])
        return True if results is not None else False

    def getByLink(self, link):
        """docstring for getLink"""
        with sqlite.connect(DB_URI) as conn:
            q = u"SELECT * FROM links WHERE link LIKE ?;"
            results = conn.execute(q, [link])
            results = results.fetchone()
        return "" if results is None else results

    def handleLink(self, submitter, desc, link):
        if self.getByLink(link) is "":
            return self.__insertLink(submitter, desc, link)
        elif self.__isLinkOld(link):
            return self.__updateLinkLastseen(link)

    def formattedPrint(self, desc, link):
        return "%s [%s]".rstrip("\n") % (desc, link)


def getLinkDescription(s):
    """
    Returns list():
        [0]  Description of a link
        [1]  Link
    """
    if len(s) <= 0 or s.find(" ") <= 0:
        return ""
    desc, link = s.rsplit(" ", 1)
    link = link.lstrip("[").rstrip("]")
    return (desc, link)

def tests():
    testlink1 = u"Vielä sananen nuorison syrjäytymisestä jaakkopyyk [http://jaakkopyyk.puheenvuoro.uusisuomi.fi/121934-viela-sananen-nuorison-syrjaytymisesta]"
    testlink2 = u"Vielä[http://jaakkopyyk.puheenvuoro.uusisuomi.fi/121934-viela-sananen-nuorison-syrjaytymisesta]"
    linkapi = LinkDBApi()

    t1 = getLinkDescription(testlink1)
    t2 = getLinkDescription(testlink2)
    assert (len(t1[0]) > 0 or len(t1[1]) > 0), "t1: FAIL"
    assert (t2 is not None or len(t2[0]) > 0 or len(t2[1]) > 0), "t2: FAIL"

    linkapi.testinit()
    #assert (linkapi.insertLink("WeeZeL", t1[0], t1[1]) == True), "FAIL \t t1 link should go to table"
    linkapi.handleLink("WeeZeL", t1[0], t1[1])
    tmp = linkapi.getByLink(t1[1])
    print linkapi.formattedPrint(tmp[2], tmp[3])

if __name__ == '__main__':
    tests()

