#got mostly from https://www.infragistics.com/community/blogs/b/torrey-betts/posts/create-an-irc-bot-using-python-2

import platform
import random
import socket
import sys
from datetime import datetime
import math

reload(sys)
sys.setdefaultencoding('utf8')

randomMsg = ["It's not the best choice, it's Spacer's Choice!",
           "You've tried the best, now try the rest!",
           "At Spacer's Choice, we cut corners so you don't have to!",
           "Spacer's Choice pre-sliced bread tastes fresh because it was!",
           "Please don't make me say anymore slogans"];
msgIndex = 0;
msgMax = 4;


server = "127.0.0.1"
channel = "#test"
botnick = "probot"

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "\nConnecting to:" + server
irc.connect((server, 6667))

irc.send('NICK ' + botnick + '\r\n')
irc.send('USER ' + botnick + ' 0 * :' + botnick + '\r\n')

irc.send("JOIN " + channel + "\n")
irc.send("PRIVMSG " + channel + " :Available Commands: !host, !ping, !time, !day, and !leave\n")

try:
  while 1:
    text = irc.recv(2048)
    if len(text) > 0:
      print text
    else:
      continue

    if text.find("PING") != -1:
      irc.send("PONG " + text.split()[1] + "\n")

#Commands start here, be sure to join the #test channel
    if text.find("PRIVMSG " + channel) != -1:
      if text.find(":!host") != -1:
        irc.send("PRIVMSG " + channel + " :" + str(platform.platform()) + "\n")
       
      if text.find(":!ping") != -1:
        irc.send("PRIVMSG " + channel + " :pong!\n")

      if text.find(":!leave") != -1:
        irc.send("PRIVMSG " + channel + " :Time to leave!\n")
        irc.send("QUIT :\n")
        sys.exit()
         
      if text.find("!time") != -1:
        irc.send("PRIVMSG " + channel + " :Current Time: " + datetime.now().strftime('%H:%M:%S') + "\n")
           
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
          
        irc.send("PRIVMSG " + channel + " :Current Day: " + day + "\n")
    elif text.find("PRIVMSG " + botnick) != -1:
      index = text.find("!")
      sender = text[1:index]
      irc.send("PRIVMSG " + sender + " :" + randomMsg[msgIndex] + "\n")
      msgIndex += 1
      if msgIndex > msgMax:
        msgIndex = 0
      

except KeyboardInterrupt:
  irc.send("QUIT :I have to go for now!\n")
  print "\n"
  sys.exit()
