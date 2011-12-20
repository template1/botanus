#!/usr/bin/python
import os
import random
import sys

import pylibconfig

from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers
from soundexpy import soundex

if len(sys.argv) != 2:
    print >> sys.stderr, "%s: usage: <config file>" % sys.argv[0]
    sys.exit(2)

# open and parse config file
config = {}
cfg = pylibconfig.Config()
filename = sys.argv[1]
if not os.path.exists(filename):
    print >> sys.stderr, "unable to open config file: %s" % filename
    sys.exit(1)
cfg.readFile(filename)

# validate
for key in ['host', 'port', 'channel', 'nick', 'modword']:
    val, valid = cfg.value(key)
    if not valid:
        print >> sys.stderr, "error: config file is missing key: %s" % key
        sys.exit(1)

    config[key] = val

soundword = soundex(config['modword'])[1:]


def connect_callback(cli):
    helpers.join(cli, config['channel'])


class MyHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        """ handle msgs """
        nick = nick[:nick.index("!")]

        modmsg = self.gen_modmsg(nick, msg)
        if modmsg is not None:
            helpers.msg(self.client, chan, modmsg)

    def gen_modmsg(self, nick, msg):
        # TODO match syllables instead of full words
        match = False
        newmsg = []
        for word in msg.split(" "):
            sword = soundex(word)
            if len(sword) > 1 and sword[1:] == soundword:
                # we have a candidate for replacement, so decide if we should
                # 66% chance if we're already replacing one word; 33% otherwise
                if match and random.randint(1, 3) != 3:
                    newmsg.append(config['modword'])
                elif random.randint(1, 3) == 3:
                    match = True
                    newmsg.append(config['modword'])
                else:
                    newsmsg.append(word)
            else:
                newmsg.append(word)

        if match:
            modmsg = "<%s> %s" % (nick, ' '.join(newmsg))
            return modmsg
        else:
            return None


cli = IRCClient(MyHandler, host=config['host'], port=config['port'],
                nick=config['nick'], connect_cb=connect_callback)
conn = cli.connect()
while True:
    conn.next()
