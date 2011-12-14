import re
import sys

if len(sys.argv) != 2:
    print "usage: %s <input file>" % sys.argv[0]
    sys.exit(1)

input = open(sys.argv[1], 'r')


def isModified(origmsg, modmsg, modword):
    """ Returns True if modmsg is origmsg, but
        with modword replacing one or more character sequences """
    origmsg, modmsg, modword = origmsg.lower(), modmsg.lower(), modword.lower()
    begin = 0
    for s in modmsg.split(modword):
        begin = origmsg.find(s, begin)
        if begin == -1:
            return False
    return True

# groups: time, nick, msg
msg_re = re.compile("^(^[0-9]{2}:[0-9]{2})\s+<[ @+]?([^>]+)>\s+(.*)$")
# matches 'nick:'
nick_re = re.compile("^[^ :]+: ")

# map compiled regexs to regex strings
# lulz can be: lal laal lol loooool haha hah hahaha rofl lmao loller* ^ ^^^
lol_res = {}
for lol_re in ["^\s*[hH][aA][haHA]*", "^\s*la+l", "^\s*lo+l",
               "^\s*rofl", "^\s*lmao", "^\s*loller", "^\s*\^+"]:
    lol_res[re.compile(lol_re)] = lol_re

# map (orignum, modnum) tuples to a map of regex strings to counts
lolcounts = {}

# list of (orignum, modnum) tuples representing the times the bot spoke
botlines = []
prevmsg, prevnum = None, None

# read the log and populate botlines for later parsing of lols
lines = input.readlines()
for num, line in enumerate(lines):
    m = msg_re.match(line)
    if m is None: continue
    time, nick, msg = m.groups()

    if nick == "dickgustao" and prevmsg is not None:
        origmsg = prevmsg

        # remove "nick:" from beginning of dickgustao's msg
        modmsg = nick_re.sub("", msg)

        if isModified(origmsg, modmsg, "dick"):
            botlines.append((prevnum, num))
        else:
            # TODO handle where we should look back more than the previous line
            pass

    prevmsg = msg
    prevnum = num

# count the number of lols for each time the bot spoke
for orignum, modnum in botlines:
    maxline = modnum + min([10, len(lines[modnum:])])
    nonlol = 0
    lolcounts[(orignum, modnum)] = {}

    # stop after 10 lines have been said or 2 non-lol lines have been said
    for line in lines[modnum + 1:modnum + maxline]:
        if nonlol == 2:
            break

        lolFound = False  # whether any of the lol regexs matched this line

        m = msg_re.match(line)
        if m is None: continue
        time, nick, msg = m.groups()

        # stop counting if a bot speaks again
        if nick == "dickgustao" or nick == "buttgustao":
            break

        for lol_re, restr in lol_res.items():
            m = lol_re.match(msg)
            if m is None:
                continue
            else:
                if restr not in lolcounts[(orignum, modnum)]:
                    lolcounts[(orignum, modnum)][restr] = 0
                lolcounts[(orignum, modnum)][restr] += 1

                lolFound = True

        if lolFound == False:
            nonlol += 1

for pair, counts in lolcounts.items():
    # prepare counts for db output
    pass
