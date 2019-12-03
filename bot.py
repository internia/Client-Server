#got mostly from https://www.infragistics.com/community/blogs/b/torrey-betts/posts/create-an-irc-bot-using-python-2

import platform
import random
import socket
import sys
from datetime import datetime
import math

randomMsg = ["It's not the best choice, it's Spacer's Choice!",
           "You've tried the best, now try the rest!",
           "At Spacer's Choice, we cut corners so you don't have to!",
           "Spacer's Choice pre-sliced bread tastes fresh because it was!",
           "Please don't make me say anymore slogans"];
msgIndex = 0;
msgMax = 4;


server = "10.0.42.17"
channel = "#test"
botnick = "probot"

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("\nConnecting to:" + server)
irc.connect((server, 6667))

irc.send(('NICK ' + botnick + '\r\n').encode('utf8'))
irc.send(('USER ' + botnick + ' 0 * :' + botnick + '\r\n').encode('utf8'))

irc.send(("JOIN " + channel + "\n").encode('utf8'))
irc.send(("PRIVMSG " + channel + " :Available Commands: !host, !ping, !time, !day, and !leave\n").encode('utf8'))

try:
  while 1:
    text = irc.recv(2048).decode('utf-8')
    if len(text) > 0:
      print(text)
    else:
      continue

    if text.find("PING") != -1:
      irc.send(("PONG " + text.split()[1] + "\n").encode('utf8'))

#Commands start here, be sure to join the #test channel
    if text.find("PRIVMSG " + channel) != -1:
      if text.find(":!host") != -1:
        irc.send(("PRIVMSG " + channel + " :" + str(platform.platform()) + "\n").encode('utf8'))
       
      if text.find(":!ping") != -1:
        irc.send(("PRIVMSG " + channel + " :pong!\n").encode('utf8'))

      if text.find(":!leave") != -1:
        irc.send(("PRIVMSG " + channel + " :Time to leave!\n").encode('utf8'))
        irc.send(("QUIT :\n").encode('utf8'))
        sys.exit()
         
      if text.find("!time") != -1:
        irc.send(("PRIVMSG " + channel + " :Current Time: " + datetime.now().strftime('%H:%M:%S') + "\n").encode('utf8'))
           
      if text.find("!day") != -1:
        dayNumber = datetime.today().weekday()

        if dayNumber == 0:
          day = "Monday"
        elif dayNumber == 1:
          day = "Tuesday"
        elif dayNumber == 2:
          day = "Wednesday"
        elif dayNumber == 3:
          day = "Thursday"
        elif dayNumber == 4:
          day = "Friday"
        elif dayNumber == 5:
          day = "Saturday"
        elif dayNumber == 6:
          day = "Sunday"
          
        irc.send(("PRIVMSG " + channel + " :Current Day: " + day + "\n").encode('utf8'))
    elif text.find("PRIVMSG " + botnick) != -1:
      index = text.find("!")
      sender = text[1:index]
      irc.send(("PRIVMSG " + sender + " :" + randomMsg[msgIndex] + "\n").encode('utf8'))
      msgIndex += 1
      if msgIndex > msgMax:
        msgIndex = 0
      

except KeyboardInterrupt:
  irc.send(("QUIT :I have to go for now!\n").encode('utf8'))
  print("\n")
  sys.exit()
