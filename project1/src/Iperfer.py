import socket
import time


def client_server(argvc):
    # Create Server
    if argvc != 4:
        print("Error: missing or additional arguments")
    if argvc[3] > 1024 or argvc[3] < 65535:
        print("Error:port number must be in the range of 1024 to 65535")
    else:
        serverName = argvc[1]
        serverPort = argvc[2]
        time = argvc[3]
        serverAddress = (serverName, serverPort)

        # Client socket Handshake 1
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connections Handshake 2
        clientSocket.connect(serverAddress)

        # Handshake 3
        while 1:
            print("Connected to server")

            # Send data in 1000 bytes
            counter = 0
            data = bytearray(1000)
            while time:
                clientSocket.sendall(data)
                counter += 1
            # Close
            clientSocket.close()

            # Calculate data
            rate = counter / 1000 / time

            print('sent={} KB rate ={} Mbps'.format(counter, rate))


def server_side(argvc):

    if argvc != 4:
        print("Error: missing or additional arguments")
    if argvc[3] > 1024 or argvc[3] < 65535:
        print("Error:port number must be in the range of 1024 to 65535")
    # Create ServerSide
    else:
        serverName = argvc[1]
        serverPort = argvc[2]
        time = argvc[3]
        serverAddress = (serverName, serverPort)

        # Server socket Handshake 1
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connection Handshake 2
        serverSocket.bind(serverAddress)

        # Listen
        serverSocket.listen(1)
        print('Listening')

        # Handshake 3
        connection_socket, addr = serverSocket.accept()

        while 1:

            chunks = connection_socket.recv(2048)
