import socket
import select

HEADER_LENGTH = 10

#ip address for server to listen on
IP = "127.0.0.2"

#tcp port number for server to listen on
PORT = 1234

#create tcp socket to use for listening to connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#deals with addresses already in use
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#bind server socket to these addresses.
server_socket.bind((IP, PORT))

#make socket listen for connections
server_socket.listen(10) 

#create list of sockets connected to the server
sockets_lists = [server_socket]

clients = {}

#debugging info
#print(f"Listening for connections on {IP}:{PORT}...")

#function which receives messages...
def receive_msg(client_socket):
	try:
		#first step to receive a message is to read the header
		message_header = client_socket.recv(HEADER_LENGTH)

		#if client closes a connection, there will be no header
		if not len(message_header):
			return False;

		#convert header to a length
		message_length = int(message_header.decode("utf-8").strip())

		#prints header and data
		return{"header": message_header, "data":client_socket.recv(message_length)}

	except:
		return False

#in a continuous loop...
while True:

	#recieve messages for all of the client sockets, then send messages to all client sockets
	read_sockets, _, exception_sockets = select.select(sockets_lists, [], sockets_lists)

	#iterates through sockets which have data to be read
	for notified_socket in read_sockets:
		#if user connecting for the first time, and connection must be accepted
		if notified_socket == server_socket:
			client_socket, client_address = server_socket.accept()
			user = receive_msg(client_socket)
			if user is False:
				continue

			#append new client socket to the socket list
			sockets_lists.append(client_socket)

			#save client username as the value to the key which is the socket object
			clients[client_socket] = user

			print("accepted new connection from {}:{}, username: {}".format(*client_address, user['data'].decode('utf-8')))

		#if not new client
	else:
		message = receive_msg(notified_socket)

		#before we attempt to read msg, make sure it exists
		if message is False:
			print("Closed connection from {}".format(clients[notified_socket]['data'].decode('utf-8')))
			sockets_lists.remove(notified_socket)
			del clients[notified_socket]
			continue

		#print message info
		user = clients[notified_socket]
		print(f"Recieved message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

		#iterate through connected clients 
		for client_socket in clients:

			#with the exception of the sender...
			if client_socket != notified_socket:
				#send user and message, both w/ headers
				client_socket.send(user['header']+user['data']+message['header']+message['data'])


	#handles socket exceptions
	for notified_socket in exception_sockets:

		#remove from list for socket
		sockets_lists.remove(notified_socket)

		#remove from list of users
		del clients[notified_socket]

	




