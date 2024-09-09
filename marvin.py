#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module for the IRC bot.

Connecting, sending and receiving messages and doing custom actions.

Keeping a log and reading incoming material.
"""
from collections import deque
from datetime import datetime
import json
import os
import re
import shutil
import socket

import chardet


#
# Settings
#
CONFIG = {
    "server":       None,
    "port":         6667,
    "channel":      None,
    "nick":         "marvin",
    "realname":     "Marvin The All Mighty dbwebb-bot",
    "ident":        None,
    "irclogfile":   "irclog.txt",
    "irclogmax":    20,
    "dirIncoming":  "incoming",
    "dirDone":      "done",
    "lastfm":       None,
}


# Socket for IRC server
SOCKET = None

# All actions to check for incoming messages
ACTIONS = []
GENERAL_ACTIONS = []

# Keep a log of the latest messages
IRCLOG = None


def getConfig():
    """
    Return the current configuration
    """
    return CONFIG


def setConfig(config):
    """
    Set the current configuration
    """
    global CONFIG
    CONFIG = config


def registerActions(actions):
    """
    Register actions to use.
    """
    print("Adding actions:")
    for action in actions:
        print(" - " + action.__name__)
    ACTIONS.extend(actions)

def registerGeneralActions(actions):
    """
    Register general actions to use.
    """
    print("Adding general actions:")
    for action in actions:
        print(" - " + action.__name__)
    GENERAL_ACTIONS.extend(actions)

def connectToServer():
    """
    Connect to the IRC Server
    """
    global SOCKET

    # Create the socket  & Connect to the server
    server = CONFIG["server"]
    port = CONFIG["port"]

    if server and port:
        SOCKET = socket.socket()
        print("Connecting: {SERVER}:{PORT}".format(SERVER=server, PORT=port))
        SOCKET.connect((server, port))
    else:
        print("Failed to connect, missing server or port in configuration.")
        return

    # Send the nick to server
    nick = CONFIG["nick"]
    if nick:
        msg = 'NICK {NICK}\r\n'.format(NICK=nick)
        sendMsg(msg)
    else:
        print("Ignore sending nick, missing nick in configuration.")

    # Present yourself
    realname = CONFIG["realname"]
    sendMsg('USER  {NICK} 0 * :{REALNAME}\r\n'.format(NICK=nick, REALNAME=realname))

    # This is my nick, i promise!
    ident = CONFIG["ident"]
    if ident:
        sendMsg('PRIVMSG nick IDENTIFY {IDENT}\r\n'.format(IDENT=ident))
    else:
        print("Ignore identifying with password, ident is not set.")

    # Join a channel
    channel = CONFIG["channel"]
    if channel:
        sendMsg('JOIN {CHANNEL}\r\n'.format(CHANNEL=channel))
    else:
        print("Ignore joining channel, missing channel name in configuration.")


def sendPrivMsg(message, channel):
    """
    Send and log a PRIV message
    """
    if channel == CONFIG["channel"]:
        ircLogAppend(user=CONFIG["nick"].ljust(8), message=message)

    msg = "PRIVMSG {CHANNEL} :{MSG}\r\n".format(CHANNEL=channel, MSG=message)
    sendMsg(msg)


def sendMsg(msg):
    """
    Send and occasionally print the message sent.
    """
    print("SEND: " + msg.rstrip('\r\n'))
    SOCKET.send(msg.encode())


def decode_irc(raw, preferred_encs=None):
    """
    Do character detection.
    You can send preferred encodings as a list through preferred_encs.
    http://stackoverflow.com/questions/938870/python-irc-bot-and-encoding-issue
    """
    if preferred_encs is None:
        preferred_encs = ["UTF-8", "CP1252", "ISO-8859-1"]

    changed = False
    enc = None
    for enc in preferred_encs:
        try:
            res = raw.decode(enc)
            changed = True
            break
        except Exception:
            pass

    if not changed:
        try:
            enc = chardet.detect(raw)['encoding']
            res = raw.decode(enc)
        except Exception:
            res = raw.decode(enc, 'ignore')

    return res


def receive():
    """
    Read incoming message and guess encoding.
    """
    try:
        buf = SOCKET.recv(2048)
        lines = decode_irc(buf)
        lines = lines.split("\n")
        buf = lines.pop()
    except Exception as err:
        print("Error reading incoming message. " + err)

    return lines


def ircLogAppend(line=None, user=None, message=None):
    """
    Read incoming message and guess encoding.
    """
    if not user:
        user = re.search(r"(?<=:)\w+", line[0]).group(0)

    if not message:
        message = ' '.join(line[3:]).lstrip(':')

    IRCLOG.append({
        'time': datetime.now().strftime("%H:%M").rjust(5),
        'user': user,
        'msg': message
    })


def ircLogWriteToFile():
    """
    Write IRClog to file.
    """
    with open(CONFIG["irclogfile"], 'w', encoding="UTF-8") as f:
        #json.dump(list(IRCLOG), f, False, False, False, False, indent=2)
        json.dump(list(IRCLOG), f, indent=2)


def readincoming():
    """
    Read all files in the directory incoming, send them as a message if
    they exists and then move the file to directory done.
    """
    if not os.path.isdir(CONFIG["dirIncoming"]):
        return

    listing = os.listdir(CONFIG["dirIncoming"])

    for infile in listing:
        filename = os.path.join(CONFIG["dirIncoming"], infile)

        with open(filename, "r", encoding="UTF-8") as f:
            for msg in f:
                sendPrivMsg(msg, CONFIG["channel"])

        try:
            shutil.move(filename, CONFIG["dirDone"])
        except Exception:
            os.remove(filename)


def mainLoop():
    """
    For ever, listen and answer to incoming chats.
    """
    global IRCLOG
    IRCLOG = deque([], CONFIG["irclogmax"])

    while 1:
        # Write irclog
        ircLogWriteToFile()

        # Check in any in the incoming directory
        readincoming()

        for line in receive():
            print(line)
            words = line.strip().split()

            if not words:
                continue

            checkIrcActions(words)
            checkMarvinActions(words)


def checkIrcActions(words):
    """
    Check if Marvin should take action on any messages defined in the
    IRC protocol.
    """
    if words[0] == "PING":
        sendMsg("PONG {ARG}\r\n".format(ARG=words[1]))

    if words[1] == 'INVITE':
        sendMsg('JOIN {CHANNEL}\r\n'.format(CHANNEL=words[3]))


def checkMarvinActions(words):
    """
    Check if Marvin should perform any actions
    """
    if words[1] == 'PRIVMSG' and words[2] == CONFIG["channel"]:
        ircLogAppend(words)

    if words[1] == 'PRIVMSG':
        raw = ' '.join(words[3:])
        row = re.sub('[,.?:]', ' ', raw).strip().lower().split()

        if CONFIG["nick"] in row:
            for action in ACTIONS:
                msg = action(row)
                if msg:
                    sendPrivMsg(msg, words[2])
                    break
        else:
            for action in GENERAL_ACTIONS:
                msg = action(row)
                if msg:
                    sendPrivMsg(msg, words[2])
                    break
