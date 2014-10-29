###
# Copyright (c) 2012, Ville Valkonen
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

from random import randint
from time import sleep

class VoiceCommander(callbacks.Plugin):
    Threaded = True

    def randomdelay(self):
        sleep(randint(2, 10))

    def voicecommander(self, irc, msg, args):
        channel = msg.args[0]
        chan = irc.state.channels[channel]

        if msg.nick not in chan.users:
            self.log.info("User %s (%s) tried to use VoiceCommander without joined any channel.", \
                            msg.nick, irc.state.nickToHostmask(msg.nick))
            return

        if not chan.isVoice(msg.nick) and not chan.isOp(msg.nick):
            irc.error("You are missing capability: op or voice")
            return

        if (len(args) == 0):
            irc.reply("Usage: @voicecommander [topic] [voice] argument(s)")
            return

        cmd = args[0]

        self.randomdelay() # Mitigate against excess flooding

        # Ability to change topic
        if cmd.lower() == "topic":
            if len(args) < 2:
                irc.error("Ehh.. forgot something? Like.... topic?")
                return

            topic = ' '.join(args[1:])
            irc.queueMsg(ircmsgs.topic(channel, topic))

        # Ability to delegate voices
        elif cmd.lower() == "voice":
            if len(args) < 2:
                irc.error("Need nick as an argument, you fool")
                return

            for whom in args[1:]:
                #whom = args[1]
                if whom not in chan.users:
                    irc.reply("Nick '%s' not in channel %s" % (whom, channel))
                    return
                #if irc.nick in irc.state.channels[channel].voices:
                #    irc.reply("Nick '%s' already voiced" % (whom))
                #    return
                irc.queueMsg(ircmsgs.voice(channel, whom))

Class = VoiceCommander


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
