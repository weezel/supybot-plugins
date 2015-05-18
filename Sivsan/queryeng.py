#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import sqlite3 as sqlite

dbname = "/home/weezel/supybot/plugins/Sivsan/sivsan.db"


class DBSearch(object):
    def __init__(self):
        self.__checkdb()

    def __checkdb(self):
        if not os.path.exists(dbname):
            raise DBnotFound("Database not found!")

    def wordequals(self, word):
        with sqlite.connect(dbname) as conn:
            q = u"SELECT word, desc FROM sivsan WHERE word LIKE ? LIMIT 10;"
            result = conn.execute(q, [word])
            return result.fetchall()

    def wordincludes(self, word):
        with sqlite.connect(dbname) as conn:
            q = u"SELECT word, desc FROM sivsan WHERE word LIKE ? LIMIT 10;"
            result = conn.execute(q, ['%' + word + '%'])
            return result.fetchall()

    def wordstartswith(self, word):
        with sqlite.connect(dbname) as conn:
            q = u"SELECT word, desc FROM sivsan WHERE word LIKE ? LIMIT 10;"
            result = conn.execute(q, [word + '%'])
            return result.fetchall()

    def wordendswith(self, word):
        with sqlite.connect(dbname) as conn:
            q = u"SELECT word, desc FROM sivsan WHERE word LIKE ? LIMIT 10;"
            result = conn.execute(q, ['%' + word])
            return result.fetchall()

    def descincludes(self, word):
        with sqlite.connect(dbname) as conn:
            q = u"SELECT word, desc FROM sivsan WHERE desc LIKE ? LIMIT 10;"
            result = conn.execute(q, ['%' + word + '%'])
            return result.fetchall()

def tests(verbose=False):
    db = DBSearch()

    if verbose: print "Word equals with: abi"
    res = db.wordequals(u"abi")
    for result in res:
        assert(result[0] == "abi")
        if verbose:
            print u"%s" % (result[0])

    if verbose: print "\nWord includes: *boli*"
    res = db.wordincludes(u"boli")
    for result in res:
        assert("boli" in result[0])
        if verbose:
            print u"%s" % (result[0])

    if verbose: print "\nWord starts with: à"
    res = db.wordstartswith(u"à")
    for result in res:
        assert(result[0][0] == u"à")
        if verbose:
            print u"%s" % (result[0])

    if verbose: print "\nWord ends with: ä"
    res = db.wordendswith(u"ä")
    for result in res:
        assert(result[0][len(result[0]) - 1] == u"ä")
        if verbose:
            print u"%s" % (result[0])

    if verbose: print "\nDescription includes: *ruumiin*"
    res = db.descincludes(u"ruumiin")
    for result in res:
        assert("ruumiin" in result[1])
        if verbose:
            print u"%s = %s" % (result[0], result[1])

if __name__ == '__main__':
    tests(verbose=True)
