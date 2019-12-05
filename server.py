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

	def set_user_stuff(self, userN, hostN, serverN, realN):
		self.realname = realN
		self.servername = serverN
		self.username = userN
		self.hostname = hostN

	def setNickname(self, newNick):
		self.nickname = newNick

	def getNickname(self):
		return self.nickname

#This function parses the user input to determine which function the execute
def parseInput(join, user, message):
	#split message by space
	messageArray = message.split()
	#if the first word of the message is join
	if messageArray[0] == "JOIN":
		#check if the start of the next word contains & or #
		if messageArray[1].__contains__("&") or messageArray[1].__contains__("#"):
			#store second word of message in temp variable
			print("aaaaaaaa")
			temp = messageArray[1]
			#store contents of temp variable from second character onwards
			channelName = temp[1:]
			join.joinchannel(user,channelName)

class Join:
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

join = Join()

outputSockets = []
messageQueues = {}

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

				input = message.split("\r\n")

				for x in range(len(input)):
					if(input[x] != ""):
						
						splitInput = input[x].split(" ")

						if(splitInput[0] == "CAP"):
							print("DATA : ", splitInput[0])

						elif(splitInput[0] == "USER"):

							if(client_socket in clients):
								user = clients[client_socket]
								user.set_user_stuff(splitInput[1], splitInput[2], splitInput[3], splitInput[4])
								#clients[client_socket].set
							else:
								clients[client_socket] = Client(client_socket, userN = splitInput[1], hostN = splitInput[2], serverN = splitInput[3], realN = splitInput[4])
								print("added", splitInput[1])
								print("client socket:", clients[client_socket])
					    #manages the joining of channels 
						elif(splitInput[0]=="JOIN"):

							print("Join channel")
							tempChannel = splitInput[1]
							channelName= tempChannel[1:]

							if((len(channelsList)==0) or channelName not in channelsList): 

								tempChannel = splitInput[1]
								channelName= tempChannel[1:]

								newChannel = Channel(user,channelName)
								channelsList.append(newChannel)

							
							user = clients[client_socket]

							index = findChannel(channelName)
							channelsList[index].add_member(user)

							nicknames = " ".join(y.nickname for y in channelsList[index].members)

							sendChannel(commandUser("JOIN " + splitInput[1], client), channelsList[index], notified_socket, sent=True )
							message=(commandServer("Error 331: NO TOPIC " +client.nickname +" ="+channelName )) + \
									(commandServer("Error 353: " +client.nickname +" ="+channelName + nicknames)) + \
									(commandServer("Error 353: END OF NAMES " +client.nickname +" ="+channelName))
							sendMsg(notified_socket, message)

						elif(splitInput[0]=="NICK"):
							if(client_socket in clients):
								user = clients[client_socket]
								user.setNickname(splitInput[1])
							else:
								clients[client_socket] = Client(client_socket, nick = splitInput[1])

						elif(splitInput[0]=="PRIVMSG"):
							if(splitInput[1][0] == "#"):
								index = findChannel(channelName)
								channel = channelsList[index]
								sendChannel(commandUser(input[x], clients[notified_socket]), channel, notified_socket)
							else:
								nickname = splitInput[1]
								for i in range(len(channel.members)):
									target = channel.members[i]
									if(target.nickname == nickname):
										sendMsg(target.socket, commandUser(input[x], clients[notified_socket]))

					else:

						print(" ")

				#before attempting to read message, make sure it exists
				if message is False:
					print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
					socketsList.remove(notified_socket)
					del clients[notified_socket]
					#continue
					
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

def sendChannel(message, channel, senderSocket, sent = False):
#find socket for each member in channel; use socket list and get sockets/users in channel
#send msg to only the sockets in channel

	for i in range(len(channel.members)):
		user = channel.members[i]
		if (sent or user.socket != senderSocket):
			sendMsg(user.socket, message)

def receiveMsg(client_socket):
	try:
		msgR = client_socket.recv(HEADER_LENGTH)
		if not len(msgR):
			return ""
		print("Message", msgR)
		return msgR.decode('utf-8')
	except:
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