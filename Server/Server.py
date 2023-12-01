import socket, Server_app
from threading import Thread

BUFFER_SIZE = 4096
SERVER_FULLHOST = socket.gethostbyname_ex(socket.gethostname())
SERVER_HOST = SERVER_FULLHOST[2][2]
SERVER_PORT = 5000
SERVER_DATABASE = {}


# Handle client request process
def request_listen(conn: socket.socket, host):
    request = conn.recv(1024).decode().split("*")
    print(request)
    if request[0] == "publish":
        file_name = request[2]
        # Check file in client local repo
        if file_name in SERVER_DATABASE[host]:
            conn.send("File already in local repo".encode())
        else:
            conn.send("Continue".encode())
        # Add file name to server database
        SERVER_DATABASE[host].append(file_name)
        print(SERVER_DATABASE)
    elif request[0] == "fetch":
        filename = request[1]
    elif request[0] == "delete":
        filename = request[1]
    elif request[0] == "discover":
        hostname = request[1]


# Listen to client on server's socket
def client_listening(host, port):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind((host, port))
    listening_socket.listen(10)
    while True:
        client_conn, client_host = listening_socket.accept()
        print(f"Accept connection from {client_host}")
        # If client have never connected to server before
        if not client_host[0] in SERVER_DATABASE:
            SERVER_DATABASE[client_host[0]] = []
        print(SERVER_DATABASE)
        file_received = Thread(target=request_listen, args=(client_conn, client_host[0]))
        file_received.start()


if __name__ == "__main__":
    print(SERVER_FULLHOST)
    Main_Socket = Thread(target=client_listening, args=(SERVER_HOST, SERVER_PORT))
    Main_Socket.start()
