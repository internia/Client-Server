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

#sending user info to server
username = my_username.encode("utf-8")
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header+username)

#iterates the sending/receiving of msgs

while True:
	message = input(f"{my_username} > ")

	if message:
		message = message.encode("utf-8")
		message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
		client_socket.send(message_header+message)

	try:	
		while True:
			#receive info
			username_header = client_socket.recv(HEADER_LENGTH)
			if not len(username_header)
				print("connection closed by server")
				sys.exit()
			username_length = int(username_length.decode("utf-8").strip())
			username = client_socket.recv(username_length).decode("utf-8")

			message_header = client_socket.recv(HEADER_LENGTH)
			message_length = int(message_header.decode("utf-8").strip())
			message = client_socket.recv(message_length).decode("utf-8")

			print(f"{username}> {message}")

	except IOError as e:
		if e.errno != errno.EAGAIN or e.errno != errno.EWOULDBLOCK:
			print('read error', str(e))
			sys.exit();
		continue
		
	except Exception as e:
		print('General error', str(e))
		sys.exit()
		pass
