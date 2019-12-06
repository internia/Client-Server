import socket
import select
import sys, time
import threading

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

#create list of channels
channelsList = []

#dictionary of clients connected 
clients = {}

def main():
	connect_server()

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


def joinchannel(self, user, channelName):
	print(channelsList)
	print(channelName)
	index = findChannel(channelName)
	if index != -1:
		irc.sendall("exists")
		channelsList[index].add_member(user)
		print(channelsList[index].members)

	else:
		irc.sendall("does not exist")
		newChannel = Channel(user,channelName)
		channelsList.append(newChannel)
		print(channelsList[index].members)


def findChannel(channelName):
	for index, Channel in enumerate(channelsList):
		if Channel.name == channelName:
			return index
	return -1


def createChannel(user, channelName):
	#Create a new instance of the Channel object
	newChannel = Channel(user,channelName)
	#Add the new channel to the list of channels
	channelsList.append(newChannel)

outputSockets = []

def connect_server():

	#in a continous loop...
	while True:

		#recieve messages for all of the client sockets, then send messages to all client sockets
		receive_sockets, _, exception_sockets = select.select(socketsList, [], socketsList)

		#iterates through sockets which have data to be read 
		for notifiedSocket in receive_sockets:

			if notifiedSocket == irc:
				
				clientSocket, client_address= irc.accept() 

				clientSocket.setblocking(0)
				
				socketsList.append(clientSocket)
			else:
				message = receiveMsg(notifiedSocket)


				if(message == ""):
					if notifiedSocket in outputSockets:
						outputSockets.remove(notifiedSocket)
					socketsList.remove(notifiedSocket)
					notifiedSocket.close()
				
				try:
					client = clients[notifiedSocket]
				except KeyError as k:
					print(k)
					pass

				splitInput = message.split("\r\n")

				for x in range(len(splitInput)):

					if(splitInput[x] != ""):
						
						splitMessage = splitInput[x].split(" ")

						if(splitMessage[0] == "CAP"):
							print("DATA : ", splitMessage[0])
							pass

						if(splitMessage[0] == "USER"):

							#if the current client is in the list of clients
							if(clientSocket in clients):
								#set variable user to the current client
								user = clients[clientSocket]
								#set user's details
								user.setUserDetails(splitMessage[1], splitMessage[2], splitMessage[3], splitMessage[4])
							else:
								#create new instance of Client object
								clients[clientSocket] = Client(clientSocket, userN = splitMessage[1], hostN = splitMessage[2], serverN = splitMessage[3], realN = splitMessage[4])
						elif(splitMessage[0]=="JOIN"):
							tempChannel = splitMessage[1]
							channelName= tempChannel[1:]
							#if the list of channels is empty or the channelName is not inthe list of channels
							if((len(channelsList)==0) or channelName not in channelsList): 
								tempChannel = splitMessage[1]
								# #set channel name to be entered channel name, ignoring the first character (#)
								channelName= tempChannel[1:]
								createChannel(user, channelName)

							else:								
								#add user to channel
								user = clients[clientSocket]
								index = findChannel(channelName)
								channelsList[index].add_member(user)

							index = findChannel(channelName)
							#Append all nicknames of all the members
							nicknames = " ".join(y.nickname for y in channelsList[index].members)

							sendToChannel(commandUser("JOIN " + splitMessage[1], client), channelsList[index], notifiedSocket, sent=True )
							message=(commandServer("Error 331: NO TOPIC " +client.nickname +" ="+channelName )) + \
									(commandServer("Error 353: " +client.nickname +" ="+channelName + nicknames)) + \
									(commandServer("Error 353: END OF NAMES " +client.nickname +" ="+channelName))
							sendMsg(notifiedSocket, message)
						elif(splitMessage[0]=="NICK"):
							if(clientSocket in clients):
								user = clients[clientSocket]
								#Set user's nickname
								user.setNickname(splitMessage[1])
							else:
								#Create a new instance of a Client object
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
					
					#iterate through connected clients
					for clientSocket in clients:
						#with the exception of the sender
						if clientSocket != notifiedSocket:
							#send user and message, both with headers
							print("aaaaa")

		#handles socket exception
		for notifiedSocket in exception_sockets:
			#remove list for socket
			socketsList.remove(notifiedSocket)
			#remove from list of users
			del clients[notifiedSocket]

def sendToChannel(message, channel, senderSocket, sent = False):
#find socket for each member in channel; use socket list and get sockets/users in channel
#send msg to only the sockets in channel

	for i in range(len(channel.members)):
		user = channel.members[i]
		if (sent or user.socket != senderSocket):
			sendMsg(user.socket, message)

def receiveMsg(clientSocket):
	try:
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