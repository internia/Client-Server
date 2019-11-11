import socket
import select
import errno

HEADER_LENGTH = 10

#ip address of the server to connect to
IP ="127.0.0.2"

#the tcp port number on the server to connect to
PORT = 1234

#takes in username input
my_username= input("Username: ")

#create tcp socket that will connect to server
client_socket = socket.socket(socket.AD_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)

#username choice for client
username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header+username)

#iterates the sending/receiving of msgs
while True:
	message = input(f"{my_username} > ")

	#before sending message, make sure message exists
	if message:
		#encode to bytes
		message = message.encode("utf-8")
		#prepare header and convert to bytes
		message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
		#then send
		client_socket.send(message_header+message)

	#eventually, errors will occur as there will be no more messages to recieve anymore
	try:	
		while True:
			#receive username and message
			username_header = client_socket.recv(HEADER_LENGTH)
			
			#if we received no data, server closes connection
			if not len(username_header)
				print("connection closed by server")
				sys.exit()

			#get the username
			username_length = int(username_length.decode("utf-8").strip())
			username = client_socket.recv(username_length).decode("utf-8")

			#get the message
			message_header = client_socket.recv(HEADER_LENGTH)
			message_length = int(message_header.decode("utf-8").strip())
			message = client_socket.recv(message_length).decode("utf-8")

			#output both together
			print(f"{username}> {message}")

	#check for error codes, if none throw up continue as normal
	except IOError as e:
		if e.errno != errno.EAGAIN or e.errno != errno.EWOULDBLOCK:
			print(read error", str(e))
			sys.exit();
		continue
	
	#Other exceptions	
	except Exception as e:
		print("General error", str(e))
		sys.exit()
		pass
