#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html
import requests

import time
import re


class FetchFailed(Exception): pass

class FMIweather(object):
    def __init__(self, city=None):
        self.city = city
        self.url = "http://ilmatieteenlaitos.fi/saa/%s?forecast=short" % city
        self.html = list()
        self.parsed = None
        self.weather = dict()
        self.celestial = unicode()

    def fetchAndParse(self):
        self.__fetch()
        self.__parseData()
        self.weather = self.__parseWeather()
        self.celestial = self.__parseCelestial()

    def __fetch(self):
        self.html = requests.get(self.url, timeout=5)

    def __parseData(self):
        self.parsed = lxml.html.fromstring(self.html.content)
        city_not_found = self.parsed.xpath( \
                '//div[@class="local-weather-error-message"]')

        if city_not_found:
            raise FetchFailed("Couldn't fetch data for '%s'" % self.city)

    def __parseWeather(self):
        d = dict()

        for tag in self.parsed.xpath('//span[@class="parameter-name-value"]'):
            name = " ".join( \
                    tag.xpath('./span[@class="parameter-name"]/text()'))
            value = " ".join( \
                    tag.xpath('./span[@class="parameter-value"]/text()'))
            d[name] = value
        return d

    def __parseCelestial(self):
        celestial = unicode()

        tmp = self.parsed.xpath('//div[@class="celestial-text"]')
        if len(tmp) > 1:
            celestial = tmp[1].text_content()
        else:
            celestial = "No celestial status."
        return celestial.lstrip(" ").rstrip(" ")

    def getForecast(self):
        return "%s [%s]" % \
               (", ".join(["%s: %s" % (key, val) \
                for key, val in self.weather.items()])
               , self.celestial)

if __name__ == '__main__':
    import sys

    fmi = FMIweather("tampere")

    fmi.fetchAndParse()
    print fmi.getForecast()

    sys.exit(1)

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Saa(callbacks.Plugin):
    threaded = True
    fmi = None

    def saa(self, irc, msg, args):
        if len(args) < 1:
            irc.reply("City missing")
            return 1

        fmi = FMIweather(args[0])

        try:
            fmi.fetchAndParse()
        except FetchFailed, ff:
            irc.error("%s" % ff)

        irc.reply(fmi.getForecast())

Class = Saa

