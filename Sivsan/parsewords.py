#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: Check whether we have the latest version of the list by counting <tr>
# values.

import re

import lxml.html
import sqlite3 as sqlite


dbname = "sivsan.db"
dbschema = "sivsan.sql"

class DBhandler(object):
    """
    Class to handle database connections.
    Don't allow direct connections for users.
    """
    def __init__(self):
        self.conn = None
        self.cur = None # Cursor

        self.initialize_db()

    def initialize_db(self):
        if self.conn == None:
            self.conn = sqlite.connect(dbname)
            self.cur = self.conn.cursor()

            with open(dbschema, "r") as f:
                sql = f.read()
                self.cur.execute(u"DROP TABLE IF EXISTS sivsan;")
                self.cur.executescript(sql)

    def insertworddesc(self, genrtr):
        self.cur.executemany(u"INSERT INTO sivsan VALUES (null, ?, ?);", genrtr)
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def insert2db(self, word, desc):
        q = u"INSERT INTO sivsan VALUES (null, ?, ?);"
        self.conn.execute(q, [word, desc])

def parsehtml2db():
    p = re.compile("\s+")
    data = list()

    data = lxml.html.parse("sivsan.html").getroot()
    for item in data.xpath("//tr"):
        word = unicode()
        desc = unicode()

        word = item.xpath("*/a[@name]/text()")[0]
        word = word.rstrip(" ")
        desc = item.cssselect("td")[0]
        desc = lxml.html.tostring(desc, method="text", encoding="unicode")
        desc = re.sub("(\s+)?=(\+s)?", "", desc)
        desc = desc.lstrip(" ").rstrip(" ")

        word = re.sub(p, " ", word)
        desc = re.sub(p, " ", desc)

        yield (word, desc)

if __name__ == '__main__':
    db = DBhandler()

    db.insertworddesc(parsehtml2db())

