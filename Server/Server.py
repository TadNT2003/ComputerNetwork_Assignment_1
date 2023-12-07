import socket
from threading import Thread

BUFFER_SIZE = 4096
SERVER_FULLHOST = socket.gethostbyname_ex(socket.gethostname())
SERVER_HOST = SERVER_FULLHOST[2][2]
SERVER_PORT = 5000
SERVER_COMMAND_PORT = 10000
SERVER_APP_PORT = 5001
SERVER_COMMAND_OUT = ""
SERVER_DATABASE = {}
CLIENT_PING_PORT = 15001


# Server discover command
def discover(hostname: str, scrap):
    global SERVER_COMMAND_OUT
    if hostname in SERVER_DATABASE:
        if len(SERVER_DATABASE[hostname]) == 0:
            return_value = f"{hostname} has not published any files"
        else:
            return_value = str(SERVER_DATABASE[hostname])
    else:
        return_value = "Host not recognize"
    SERVER_COMMAND_OUT = return_value
    # print(return_value)


def ping(hostname: str, scrap):
    global SERVER_COMMAND_OUT
    if hostname in SERVER_DATABASE:
        client_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_connect.settimeout(10)
        try:
            client_connect.connect((hostname, CLIENT_PING_PORT))
            client_connect.send("ping from server".encode())
            response = client_connect.recv(1024).decode()
            # print(response)
        except TimeoutError:
            SERVER_COMMAND_OUT = "Request time out"
        except ConnectionError:
            SERVER_COMMAND_OUT = "Host unreachable"
        else:
            if response == "acknowledge":
                SERVER_COMMAND_OUT = f"Ping to {hostname}. Acknowledge received!"
        client_connect.close()
    else:
        SERVER_COMMAND_OUT = "Host not recognize"


# Handle client request process
def request_listen(conn: socket.socket, host):
    request = conn.recv(1024).decode().split("*")
    host = request[0]
    # Publish command
    if request[1] == "publish":
        file_name = request[3]
        # print(file_name)
        # Check file in client local repo
        if file_name in SERVER_DATABASE[host]:
            conn.send("File already in local repo".encode())
        else:
            conn.send("Continue".encode())
            # Add file name to server database
            SERVER_DATABASE[host].append(file_name)
            # print(SERVER_DATABASE)
    # Fetch command
    elif request[1] == "fetch":
        file_name = request[2]
        # Check file in client local repo
        if file_name in SERVER_DATABASE[host]:
            conn.send("File already in local repo".encode())
        else:
            # conn.send("Continue".encode())
            # Find the client with the file
            found = False
            for i in SERVER_DATABASE:
                if file_name in SERVER_DATABASE[i]:
                    conn.send(str(i).encode())
                    found = True
                    break
            if not found:
                # If server cannot find file in DB
                conn.send("File not recognize".encode())
            else:  # Publish the file to server DB of requested client
                # Add file name to server database
                SERVER_DATABASE[host].append(file_name)
                # print(SERVER_DATABASE)
    # Delete command
    elif request[1] == "delete":
        file_name = request[2]
        # Check file in client local repo
        if file_name in SERVER_DATABASE[host]:
            SERVER_DATABASE[host].remove(file_name)
            conn.send("Delete successfully".encode())
        else:
            conn.send("Cannot delete! File not in local repo".encode())
    # Discover command
    elif request[1] == "discover":
        hostname = request[2]
        dis_result: str
        # Find host in server DB
        if hostname in SERVER_DATABASE:
            if len(SERVER_DATABASE[hostname]) == 0:
                dis_result = f"{hostname} has not published any files"
            else:
                dis_result = str(SERVER_DATABASE[hostname])
        else:
            dis_result = "Host not recognize"
        conn.send(dis_result.encode())
    # List client command
    elif request[1] == "list":
        client_list = ""
        for i in SERVER_DATABASE:
            if client_list != "":
                client_list = client_list + "*" + str(i)
            else:
                client_list = str(i)
        conn.send(client_list.encode())


# Listen to client on server's socket
def client_listening(host, port):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind((host, port))
    listening_socket.listen(10)
    while True:
        client_conn, client_host = listening_socket.accept()
        print(f"Accept connection from {client_host}")

        request_handle = Thread(target=request_listen, args=(client_conn, client_host[0]))
        request_handle.start()


# Use for handling command
def command_handling(conn: socket.socket, host):
    command = conn.recv(1024).decode().split("*")
    if command[0] == "discover":
        hostname = command[1]
        discover(hostname, 1)
        conn.send(SERVER_COMMAND_OUT.encode())
    elif command[0] == "ping":
        hostname = command[1]
        # print(command)
        for i in range(4):
            ping(hostname, 1)
            # print(SERVER_COMMAND_OUT)
            conn.send(SERVER_COMMAND_OUT.encode())
            reply_from_app = conn.recv(1024).decode()


# Use for listening command
def command_listening(host, port):
    command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    command_socket.bind((host, port))
    command_socket.listen(10)
    while True:
        command_conn, addr = command_socket.accept()
        command_handle = Thread(target=command_handling, args=(command_conn, addr))
        command_handle.start()


def app_connect(host, port):
    app_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    app_socket.bind((host, port))
    app_socket.listen(10)
    while True:
        app_conn, addr = app_socket.accept()
        client_host = app_conn.recv(1024).decode()
        # If client have never connected to server before
        if not client_host in SERVER_DATABASE:
            SERVER_DATABASE[client_host] = []
            # print(SERVER_DATABASE)


if __name__ == "__main__":
    # print(SERVER_FULLHOST)
    # Thread for listening to client
    Main_Socket = Thread(target=client_listening, args=(SERVER_HOST, SERVER_PORT))
    Main_Socket.start()

    # Thread for client app
    App_Socket = Thread(target=app_connect, args=(SERVER_HOST, SERVER_APP_PORT))
    App_Socket.start()

    # Thread for listening to command
    Command_Socket = Thread(target=command_listening, args=(SERVER_HOST, SERVER_COMMAND_PORT))
    Command_Socket.start()
