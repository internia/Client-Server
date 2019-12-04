import socket
import select

HEADER_LENGTH =10

#ip address for server to listen on
IP= "10.0.42.17"
#tcp port number for server to listen to
PORT= 1234

#create TCP server to use for listening to connections
server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
#bind server socket to these addresses
server_socket.bind((IP, PORT))
#make socket listen for connections
server_socket.listen()

print(f"Server established via Port:" + str(PORT))

#create list of sockets connected to the server
sockets_list=[server_socket]

#dictionary of clients connected 
clients = {}

#create list of channels
channelsList = []


class Channel():
    members = []
    name = ""

    def __init__(self, user, name):
        self.name = name
        self.members.append(user)

    def add_member(self, user):
        self.members.append(user)

    def channelMsg():
    	#for every client socket in members list


#functions which recieves messages...
def receive_message(client_socket):
    try:
    	#first step to receive message is to read the header
    	message_header= client_socket.recv(HEADER_LENGTH)

    	#if connection closes, there is no header
        if not len(message_header):
            return False

        #convert header to a length
        message_length= int(message_header.decode("utf-8").strip())

        #prints header and data
        return {"header": message_header, "data": client_socket.recv(message_length)}

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
			print("exists")
			channelsList[index].add_member(user)
			print(channelsList[index].members)
		else:
			print("does not exist")
			newChannel = Channel(user,channelName)
			channelsList.append(newChannel)
			print(channelsList[index].members)


def findChannel(channelName):
    for index, Channel in enumerate(channelsList):
        if Channel.name == channelName:
            return index
    return -1

test = Test()
#in a continous loop...
while True:
    #recieve messages for all of the client sockets, then send messages to all client sockets
	read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    #iterates through sockets which have data to be read 
	for notified_socket in read_sockets:
		if notified_socket == server_socket:
			client_socket, client_address= server_socket.accept()

			user = receive_message(client_socket)
			if user is False:
				continue
            
            #append new client to socket list
			sockets_list.append(client_socket)
            
            #save client username as the value to the key which is the socket object
			clients[client_socket] = user

			#accepted connection from: username
			print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

		#if not new client
		else:
			message= receive_message(notified_socket)

			#before attempting to read message, make sure it exists
			if message is False:
				print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
				sockets_list.remove(notified_socket)
				del clients[notified_socket]
				continue

			#print message info
			user = clients[notified_socket]
			print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
			print(f"{user['data'].decode('utf-8')}, {message['data'].decode('utf-8')}")
			parseInput(test, f"{user['data'].decode('utf-8')}", f"{message['data'].decode('utf-8')}")

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


#find socket for each member in channel; use socket list and get sockets/users in channel
#send msg to only the sockets in channel
