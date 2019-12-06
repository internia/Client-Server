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
#create list of sockets for outputs
outputSockets = []
#create list of channels
channelsList = []
#dictionary of clients connected 
clients = {}
#dictionary of messages
messageQueues = {}

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

def connect_server():

	#in a continous loop...
	while True:

		#recieve messages for all of the client sockets, then send messages to all client sockets
		receive_sockets, _, exception_sockets = select.select(socketsList, [], socketsList)

		#iterates through sockets which have data to be read 
		for notified_socket in receive_sockets:

			if notified_socket == irc:
				
				client_socket, client_address= irc.accept() 

				client_socket.setblocking(0)
				
				socketsList.append(client_socket)
			else:
				message = receiveMsg(notified_socket)


				if(message == ""):
					if notified_socket in outputSockets:
						outputSockets.remove(notified_socket)
					socketsList.remove(notified_socket)
					notified_socket.close()
				
				try:
					client = clients[notified_socket]
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
							if(client_socket in clients):
								#set variable user to the current client
								user = clients[client_socket]
								#set user's details
								user.setUserDetails(splitMessage[1], splitMessage[2], splitMessage[3], splitMessage[4])
							else:
								#create new instance of Client object
								clients[client_socket] = Client(client_socket, userN = splitMessage[1], hostN = splitMessage[2], serverN = splitMessage[3], realN = splitMessage[4])
						elif(splitMessage[0]=="JOIN"):
							
							joinChannel(client_socket, splitMessage, message, user, client)

						elif(splitMessage[0]=="NICK"):
							
							if(client_socket in clients):
								user = clients[client_socket]
								#Set user's nickname
								user.setNickname(splitMessage[1])
							else:
								#Create a new instance of a Client object
								clients[client_socket] = Client(client_socket, nick = splitMessage[1])

						elif(splitMessage[0]=="PRIVMSG"):
							
							sendPrivMsg()
					else:

						print(" ")

				#before reading message, make sure it exists
				if message is False:
					print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
					socketsList.remove(notified_socket)
					del clients[notified_socket]
					
					#iterate through connected clients
					for client_socket in clients:
						#with the exception of the sender
						if client_socket != notified_socket:
							#send user and message, both with headers
							print("aaaaa")

		#handles socket exception
		for notified_socket in exception_sockets:
			#remove list for socket
			socketsList.remove(notified_socket)
			#remove from list of users
			del clients[notified_socket]


def joinChannel(client_socket, splitMessage, message, user, client):
	
	tempChannel = splitMessage[1]
	channelName= tempChannel[1:]
	#if the list of channels is empty or the channelName is not inthe list of channels

	#creatchannel funct
	user = clients[client_socket]
	index = findChannel(channelName)
	channelsList[index].add_member(user)

	#Append all nicknames of all the members
	nicknames = " ".join(y.nickname for y in channelsList[index].members)

	sendToChannel(commandUser("JOIN " + splitMessage[1], client), channelsList[index], notified_socket, sent=True )
	message=(commandServer("Error 331: NO TOPIC " +client.nickname +" ="+channelName )) + \
			(commandServer("Error 353: " +client.nickname +" ="+channelName + nicknames)) + \
			(commandServer("Error 353: END OF NAMES " +client.nickname +" ="+channelName))
	sendMsg(notified_socket, message)

def sendToChannel(message, channel, senderSocket, sent = False):
#find socket for each member in channel; use socket list and get sockets/users in channel
#send msg to only the sockets in channel

	for i in range(len(channel.members)):
		user = channel.members[i]
		if (sent or user.socket != senderSocket):
			sendMsg(user.socket, message)

def findChannel(channelName):
	for index, Channel in enumerate(channelsList):
		if Channel.name == channelName:
			return index
	return -1

def receiveMsg(client_socket):
	try:
		msgR = client_socket.recv(HEADER_LENGTH)
		if not len(msgR):
			return ""
		return msgR.decode('utf-8')
	except:
		return ""
		pass
def sendPrivMsg(splitMessage):
	if(splitMessage[1][0] == "#"):
		#find the channel mentioned in the list and store the index
		index = findChannel(channelName)
		#store the found channel in the channel variable
		channel = channelsList[index]
		#send message to channel
		sendToChannel(commandUser(splitInput[x], clients[notified_socket]), channel, notified_socket)
	else:
		nickname = splitMessage[1]
		#find member by nickname by iterating through all members
		for i in range(len(channel.members)):
			#store current member being iterated through in memberIndex variable
			memberIndex = channel.members[i]
			#if the member's nickname matches the nickname being searched for
			if(memberIndex.nickname == nickname):
				#send message to that member
				sendMsg(memberIndex.socket, commandUser(splitInput[x], clients[notified_socket]))
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