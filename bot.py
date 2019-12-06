import platform
import random
import sys
import socket
from datetime import datetime
import math

#Each message will be sent in order, then loop
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

#Create the socket
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("\nConnecting to:" + server)
#Connect to the srver
irc.connect((server, 6667))

#Connection Registration
irc.send(('NICK ' + botnick + '\r\n').encode('utf8'))
irc.send(('USER ' + botnick + ' 0 * :' + botnick + '\r\n').encode('utf8'))

#Join the #test channel and send introduction message
irc.send(("JOIN " + channel + "\n").encode('utf8'))
irc.send(("PRIVMSG " + channel + " :Available Commands: !ping, !time, !day, and !leave\n").encode('utf8'))

try:
  while 1:
    #Reveive messages from server
    text = irc.recv(2048).decode('utf-8')
    if len(text) > 0:
      print(text)
    else:
      continue
    
    #Respond to PINGs from the server
    if text.find("PING") != -1:
      irc.send(("PONG " + text.split()[1] + "\n").encode('utf8'))

    #Channel Commands
    if text.find("PRIVMSG " + channel) != -1:
      #Respond to pings from other users
      if text.find(":!ping") != -1:
        irc.send(("PRIVMSG " + channel + " :pong!\n").encode('utf8'))
      
      #Disconnects the bot and exits
      if text.find(":!leave") != -1:
        irc.send(("PRIVMSG " + channel + " :Time to leave!\n").encode('utf8'))
        irc.send(("QUIT :\n").encode('utf8'))
        sys.exit()
      
      #Give the current time
      if text.find("!time") != -1:
        irc.send(("PRIVMSG " + channel + " :Current Time: " + datetime.now().strftime('%H:%M:%S') + "\n").encode('utf8'))
      
      #Give the current day
      if text.find("!day") != -1:
        dayNumber = datetime.today().weekday()
        
        #Translate the number from datetime.today().weekday() into the proper day
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
    
    #Respond to private messages from other users with a corporate slogan
    elif text.find("PRIVMSG " + botnick) != -1:
      index = text.find("!") #find index of the end of the user's name
      sender = text[1:index] #get the user's name from their message
      irc.send(("PRIVMSG " + sender + " :" + randomMsg[msgIndex] + "\n").encode('utf8')) #send the slogan
      
      #Increment the slogans index, and loop back if neccesary
      msgIndex += 1 
      if msgIndex > msgMax:
        msgIndex = 0
      
#Disconnect if the program is closed
except KeyboardInterrupt:
  irc.send(("QUIT :I have to go for now!\n").encode('utf8'))
  print("\n")
  sys.exit()
