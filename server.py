import socket
import select
import sys, time

HEADER_LENGTH =400

#ip address for server to listen on
IP= "10.0.42.17"
#tcp port number for server to listen to
PORT= 6667

#create TCP server to use for listening to connections
irc= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
#bind server socket to these addresses
irc.bind((IP, PORT))
#make socket listen for connections
irc.listen()

print(f"Server established via Port:" + str(PORT))

#create list of sockets connected to the server
socketsList=[irc]

#create list of socketsfor holding output
outputSockets = []

#create list of channels
channelsList = []

#dictionary of clients connected 
clients = {}

def main():
	connect_server()

#client class initialises/gets/sets all the variables used to deal with the clients
class Client():
	
	def __init__(self, socket, nick=None, userN=None, hostN=None, serverN=None, realN=None):
		self.nickname = nick
		self.realname = realN
		self.servername = serverN
		self.username = userN
		self.hostname = hostN
		self.socket = socket

	def setUserDetails(self, userN, hostN, serverN, realN):
		self.realname = realN
		self.servername = serverN
		self.username = userN
		self.hostname = hostN

	def setNickname(self, newNick):
		self.nickname = newNick

	def getNickname(self):
		return self.nickname

#channel class initialises the channel members and names, and creates function which allows us to add members
class Channel():
	#create list of members
	members = []
	#channel name
	name = ""

	#initialising the variables used in the class
	def __init__(self, user, name):
		self.name = name
		self.members.append(user)

	#when this method is called, add new member to the channel member list
	def add_member(self, user):
		self.members.append(user)


def findChannel(channelName):
	#for every element in channelsList
	for index, Channel in enumerate(channelsList):
		#If the name of the channel is equal to channelName
		if Channel.name == channelName:
			#return the index of the channel element in the list
			return index
	#if not found return -1
	return -1


def createChannel(user, channelName):
	#Create a new instance of the Channel object
	newChannel = Channel(user,channelName)
	#Add the new channel to the list of channels
	channelsList.append(newChannel)


def connect_server():

	#in a continous loop...
	while True:

		#recieve messages for all of the client sockets, then send messages to all client sockets
		receiveSockets, _, exceptionSockets = select.select(socketsList, [], socketsList)

		#iterates through sockets which have data to be read 
		for notifiedSocket in receiveSockets:

			if notifiedSocket == irc:
				
				clientSocket, clientAddress= irc.accept() 

				clientSocket.setblocking(0)
				
				socketsList.append(clientSocket)
			else:
				message = receiveMsg(notifiedSocket)

				#If the message is empty
				if(message == ""):
					#if notifiedSocket is in outputSockets
					if notifiedSocket in outputSockets:
						#remove notifiedSockets from outputSockets
						outputSockets.remove(notifiedSocket)
					#remove notifiedSockets from socketsList
					socketsList.remove(notifiedSocket)
					notifiedSocket.close()
				
				try:
					client = clients[notifiedSocket]
				except KeyError as k:
					print(k)
					pass

				#Split the input by line
				splitInput = message.split("\r\n")

				#For every line of the input
				for x in range(len(splitInput)):

					#If input is empty
					if(splitInput[x] != ""):
						#Split input line by space
						splitMessage = splitInput[x].split(" ")
						#If command is USER
						if(splitMessage[0] == "USER"):
							#if the current client is in the list of clients
							if(clientSocket in clients):
								#set variable user to the current client
								user = clients[clientSocket]
								#set user's details (username, nickname etc.) from parameters provided in hexchat
								user.setUserDetails(splitMessage[1], splitMessage[2], splitMessage[3], splitMessage[4])
							else:
								#create new instance of Client object
								clients[clientSocket] = Client(clientSocket, userN = splitMessage[1], hostN = splitMessage[2], serverN = splitMessage[3], realN = splitMessage[4])
						#If command is JOIN
						elif(splitMessage[0]=="JOIN"):
							#temp variable to hold second value in the array after the JOIN command
							tempChannel = splitMessage[1]
							#Sets channelName to tempChannel but ignoring the first character (#)
							channelName= tempChannel[1:]
							#if the list of channels is empty or the channelName is not inthe list of channels
							if((len(channelsList)==0) or channelName not in channelsList): 
								#Creates new channel
								createChannel(user, channelName)

							else:								
								#store current client in user variable
								user = clients[clientSocket]
								#finds index of channel being searched for
								index = findChannel(channelName)
								#adds user to the indexed channel in channelsList
								channelsList[index].add_member(user)

							index = findChannel(channelName)
							#Append all nicknames of all the members in the channel
							nicknames = " ".join(y.nickname for y in channelsList[index].members)

							#Sends join command from user to the channel
							sendToChannel(commandUser("JOIN " + splitMessage[1], client), channelsList[index], notifiedSocket, sent=True )
						#If command is NICK
						elif(splitMessage[0]=="NICK"):
							#If the current client is in the clients dictionary
							if(clientSocket in clients):
								#Set current client to user variable
								user = clients[clientSocket]
								#Set user's nickname using parameter provided by hexchat
								user.setNickname(splitMessage[1])
							else:
								#Create a new instance of a Client object and add it to the clients dictionary
								clients[clientSocket] = Client(clientSocket, nick = splitMessage[1])

						elif(splitMessage[0]=="PRIVMSG"):
							if(splitMessage[1][0] == "#"):
								#find the channel mentioned in the list and store the index
								index = findChannel(channelName)
								#store the found channel in the channel variable
								channel = channelsList[index]
								#send message to channel
								sendToChannel(commandUser(splitInput[x], clients[notifiedSocket]), channel, notifiedSocket)
							else:
								nickname = splitMessage[1]
								#find member by nickname by iterating through all members
								for i in range(len(channel.members)):
									#store current member being iterated through in memberIndex variable
									memberIndex = channel.members[i]
									#if the member's nickname matches the nickname being searched for
									if(memberIndex.nickname == nickname):
										#send message to that member
										sendMsg(memberIndex.socket, commandUser(splitInput[x], clients[notifiedSocket]))
					else:
						print(" ")

				#before reading message, make sure it exists
				if message is False:
					print(f"Closed connection from {clients[notifiedSocket]['data'].decode('utf-8')}")
					socketsList.remove(notifiedSocket)
					del clients[notifiedSocket]

		#handles socket exception
		for notifiedSocket in exceptionSockets:
			#remove list for socket
			socketsList.remove(notifiedSocket)
			#remove from list of users
			del clients[notifiedSocket]

def sendToChannel(message, channel, senderSocket, sent = False):
	#loop through every member in the channel
	for i in range(len(channel.members)):
		#set variable to user to the current member in th channel
		user = channel.members[i]
		#If the user is not yourself
		if (sent or user.socket != senderSocket):
			#Send message to user
			sendMsg(user.socket, message)

def receiveMsg(clientSocket):
	try:
		#Receive header length
		msgR = clientSocket.recv(HEADER_LENGTH)
		if not len(msgR):
			return ""
		return msgR.decode('utf-8')
	except:
		return ""
		pass

def sendMsg(socket, message):
	print ("Send: " + message.decode('utf-8'))
	socket.send(message)

def commandServer(message):
	return(":"+ socket.gethostname() + ""+ message+ "\r\n").encode("utf-8")

def commandUser(message, client):
	j = client.nickname + "!" + client.username + "@" + client.servername
	return (":" + j + " " + message + "\r\n").encode("utf-8")

if __name__ == '__main__':
	main()