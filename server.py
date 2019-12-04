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
sockets_list=[irc]

#dictionary of clients connected 
clients = {}

#create list of channels
channelsList = []

def main():
	connect_server()


class Channel():
	members = []
	name = ""

	def __init__(self, user, name):
		self.name = name
		self.members.append(user)

	def add_member(self, user):
		self.members.append(user)

class Client():
	
	def __init__(self, socket, nick=None, userN=None, hostN=None, serverN=None, realN=None):
		self.nickname = nick
		self.realname = realN
		self.servername = serverN
		self.username = UserN
		self.hostname = hostN
		self.socket = socket



def receive_message(client_socket):
	try:
		#first step to receive message is to read the header
		message_header= client_socket.recv(HEADER_LENGTH)
		#if connection closes, there is no header
		if not len(message_header):
			return False

		#convert header to a length
		message_length= int(message_header.decode("utf-8").strip())

		#Accepted connection from 10.0.42.19:52221.
		#[10.0.42.19:52221] -> b'CAP LS 302\r\n'
		#[10.0.42.19:52221] -> b'NICK qmbuser\r\nUSER qmbuser qmbuser 10.0.42.17 :realname\r\n'


		#prints header and data
		return {"header": message_header, "data": client_socket.recv(message_length)}
		print(('NICK ' + botnick + '\r\n').encode('utf8'))


	except:
		return False



def parseInput(test, user, message):
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
			test.joinchannel(user,channelName)

class Test:
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

test = Test()

def connect_server():

	#in a continous loop...
	while True:

		#recieve messages for all of the client sockets, then send messages to all client sockets
		receive_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

		#iterates through sockets which have data to be read 
		for notified_socket in receive_sockets:

			if notified_socket == irc:
				
				client_socket, client_address= irc.accept() 

				client_socket.setblocking(0)
				
				user = receive_message(client_socket)

				#append new client to socket list
				sockets_list.append(client_socket)
				
				#save client username as the value to the key which is the socket object
				clients[client_socket] = user

			#if not new client
			else:
				message = receive_message(notified_socket)

				input = message.split("\r\n")

				for x in range(len(input)):
					if(input[x] != ""):
						splitInput = input[x].split(" ")

					if(splitInput[0] == "CAP"):
						print("DATA : ", splitInput[0])
					elif(splitInput[0] == "USER"):
						if(client_socket in clients):
							clients[client_socket].set
						else:
							print("added", splitInput[1])
							print("client socket:", clients[client_socket])

					elif(splitInput[0]=="JOIN"):
						print("Join channel")
						tempChannel = splitInput[1]
						channelName= tempChannel[1:]

						if((len(channelsList)==0) or channelName not in channelsList): 

							tempChannel = splitInput[1]
							channelName= tempChannel[1:]

							channel = Channel(channelName)

							channelsList[channelName]= channel


						try:
							user = clients[client_socket]
						except KeyError as k:
							print(k)

						channelsList[channelName].addUser(user)

						nick = "".join(u.nickn for u in channelsList[channelName].members)

						sendChannel(commandUser("JOIN " + splitInput[1], client), channelsList[channelName], notified_socket, sent =True )
						message=(commandServer("Error 331: " +client.nickname +" ="+channelName +" :No topic is set")) + \
								(commandServer("Error 353: " +client.nickname +" ="+channelName + nick )) + \
								(commandServer("Error 353: " +client.nickname +" ="+channelName +" End of names"))
						sendMsg(notified_socket, message)

					elif(splitInput[0]=="NICK"):
						if(client_socket in clients):
							clients[client_socket].setNick(splitInput[1])
						else:
							clients[client_socket].Client(client_socket, nickn = splitInput[1])

					elif(splitInput[0]=="PRIVMSG"):
						if(splitInput[1][0] == "#"):
							channel = channelsList[channelName]
							sendChannel(commandUser(input[x], clients[notified_socket]))
						else:
							nickname = splitInput[1]
							for i in range(len(channel.members)):
								target = channel.members[i]
								if(target.nickname == nickname):
									sendMsg(target.socket, commandUser(input[x], clients[notified_socket]))

					else:

						print("ERROR")

				#before attempting to read message, make sure it exists
				if message is False:
					print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
					sockets_list.remove(notified_socket)
					del clients[notified_socket]
					continue
					
					#iterate through connected clients
					for client_socket in clients:
						#with the exception of the sender
						if client_socket != notified_socket:
							#send user and message, both with headers
							client_socket.send(user['header']+ user['data']+ message['header']+ message['data'])

		#handles socket exception
		for notified_socket in exception_sockets:
			#remove list for socket
			sockets_list.remove(notified_socket)
			#remove from list of users
			del clients[notified_socket]

def sendChannel(message, Channel, senderSocket, send=False):
#find socket for each member in channel; use socket list and get sockets/users in channel
#send msg to only the sockets in channel

	for i in range(len(channels.members)):
		user = channel.members[i]
		if (send or client.socket != senderSocket):
			sendMsg(client.socket, message)

def receiveMsg(client_socket):
	try:
		msgR = client_socket.recv(HEADER_LENGTH)
		if not len(msgR):
			return ""
		print("Message", msgR)
		return msgR.decode('utf-8')
	except:
		pass

def commandServer(message):
	return(":"+ socket.gethostname() + ""+ message+ "\r\n").encode("utf-8")

def commandUser(message, client):
	j = client.nickname + "!" + client.username + "@" + client.servername


def sendMsg(socket, message):
	print ("Send: " + message.decode('utf-8'))
	socket.send(message)


	
if __name__ == '__main__':
	main()