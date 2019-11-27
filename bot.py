#got mostly from https://www.infragistics.com/community/blogs/b/torrey-betts/posts/create-an-irc-bot-using-python-2

import platform
import random
import socket
import sys

reload(sys)
sys.setdefaultencoding('utf8')

server = "127.0.0.1"
channel = "#test"
botnick = "bot"
sentUser = False
sentNick = False

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "\nConnecting to:" + server
irc.connect((server, 6667))

try:
   while 1:
      text = irc.recv(2048)
      if len(text) > 0:
         print text
      else:
         continue

      if text.find("PING") != -1:
         irc.send("PONG " + text.split()[1] + "\n")

      if sentUser == False:
         irc.send("USER " + botnick + " " + botnick + " " + botnick + " :This is a fun bot\n")
         sentUser = True
         continue

      if sentUser and sentNick == False:
         irc.send("NICK " + botnick + "\n")
         sentNick = True
         continue

      if text.find("255 " + botnick) != -1:
         irc.send("JOIN " + channel + "\n")
         irc.send("PRIVMSG " + channel + " :Available Commands: !host, !ping, and !leave\n")

#Commands start here, be sure to join the #test channel

      if text.find(":!host") != -1:
         irc.send("PRIVMSG " + channel + " :" + str(platform.platform()) + "\n")
		 
      if text.find(":!ping") != -1:
         irc.send("PRIVMSG " + channel + " :pong!\n")

      if text.find(":!leave") != -1:
         irc.send("PRIVMSG " + channel + " :Time to leave!\n")
         irc.send("QUIT :\n")
         sys.exit()

except KeyboardInterrupt:
   irc.send("QUIT :I have to go for now!\n")
   print "\n"
   sys.exit()