import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.2"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setssockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen() 

sockets_lists = [server_socket]

clients = {}

def receive_msg(client_socket):
	try:
		message_header = client_socket.recv(HEADER_LENGTH)

		if not len(message_header):
			return False;

		message_length = int(message_header.decode("utf-8").strip())
		return{"header": message_header, "data:" client_socket.revc(message_length)}

	except:
		return False


while True:
	read_sockets, _, exception_sockets = select.select(sockets_lists, [], sockets_lists)

	for notified_socket in read_sockets:
		#if user connecting for the first time, and connection must be accepted
		if notified_socket == server_socket:
			client_socket, client_address - server_socket.accept()

			user = receive_msg(client_socket)
			if user is False:
				continue

			sockets_lists.append(client_socket)

			clients[client_socket] = user

			print(f"accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data'].decode('utf-8')}")

		#if not new client
	else:
		message = receive_msg(notified_socket)

		if message is False:
			print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
			sockets_lists.remove(notified_socket)
			del clients[notified_socket]
			continue

		user = clients[notified_socket]
		print(f"Recieved message from: {user['data'].decode('utf-8')}")

		#sending msg to all users apart from sender
		for client_socket in clients:
			if client_socket != notified_socket:
				client_socket.send(user['header']+user['data']+message['header']+message['data'])


	for notified_socket in exception_sockets:
		sockets_lists.remove(notified_socket)
		del clients[notified_socket]

	




