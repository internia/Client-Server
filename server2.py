import socket
import select

HEADER_LENGTH =10

IP= "127.0.0.1"
PORT= 1234


server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list=[server_socket]

clients = {}

channelsList = {}


class Channel():
    members = {}
    name = ""
    def __init__(self, user, name):
        self.name = name
        self.members.append(user)

    def add_member(self, user):
        self.members.add(user)

    def joinchannel(self, user, channelName):
        if channelName in channelsList:
            print("exists")
        else:
            print("does not exist")
            newChannel = Channel(user,channelName)
            self.channelsList.append(newChannel)
            print("created")



def receive_message(client_socket):
    try:
        message_header= client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False

        message_length= int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False

def parseInput(self, user, message):
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
            #joinchannel(user,channelName)
            if channelName in channelsList:
                print("exists")
            else:
                print("does not exist")
                newChannel = Channel(user,channelName)
                self.channelsList.append(newChannel)
                print("created")

def runServer():
    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address= server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)
            clients[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

        else:
            message= receive_message(notified_socket)
            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user= clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
            print(f"{user['data'].decode('utf-8')}, {message['data'].decode('utf-8')}")
            parseInput(f"{user['data'].decode('utf-8')}", f"{message['data'].decode('utf-8')}")

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header']+ user['data']+ message['header']+ message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]


# 
# def main():
#     runServer()
#
# if __name__ == '__main__':
#     main()
