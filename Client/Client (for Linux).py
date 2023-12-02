import os
import socket
from threading import Thread

BUFFER_SIZE = 4096
SERVER_HOST = "192.168.31.48"
SERVER_PORT = 5000
# Linux client will update host down the line, while Window user can get it right now
CLIENT_HOST = socket.gethostbyname(socket.gethostname())
CLIENT_PORT = 15000


def receive_file(conn, fname):
    if fname == "":
        # Use when publish
        filename = conn.recv(1024).decode()
        reply = "ready for transferring"
    else:
        # Use when fetch
        filename = fname
        reply = fname
    # print(file_info)
    # filename, filesize = file_info.split("*")
    # filesize = file_info[1]

    conn.send(reply.encode())
    with open(filename, "wb", 0) as received_file:
        while True:
            # Receive file from client that send it
            bytes_read = conn.recv(BUFFER_SIZE)
            # If end of file
            if not bytes_read:
                break
            # Write it on local file
            received_file.write(bytes_read)
        # Ensure to write the file directly to disk
        received_file.flush()
        os.fsync(received_file.fileno())


def publish(lname: str, fname: str):
    # Initialize connection to server
    global published_file, CLIENT_HOST
    server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connect.connect((SERVER_HOST, SERVER_PORT))
    # Update true IP use for connection of Linux client
    CLIENT_HOST = server_connect.getsockname()[0]
    # Linux client use "/", Window client use "\\"
    if lname != "":
        full_filename = lname + "/" + fname
    else:
        full_filename = fname
    # print(full_filename)
    # Catch error with open file
    try:
        published_file = open(full_filename, "rb")
    except IOError:
        print("File not exist")
    else:
        # Send command request to server
        request = "publish*" + lname + "*" + fname
        server_connect.send(request.encode())
        # Waiting for server to check file in local repo
        while True:
            check_local = server_connect.recv(1024).decode()
            if check_local:
                break
        # print(check_local)
        if check_local == "Continue" and lname != "":  # Only when server don't have file info AND it's not actually in local repo
            # Add file from system file to local repo
            # Connect to itself to transfer file from file system to local repo
            self_connect = socket.socket()
            self_connect.connect((CLIENT_HOST, CLIENT_PORT))
            # filesize = os.path.getsize(full_filename)
            self_connect.send(f"{fname}".encode())
            reply = self_connect.recv(1024).decode()
            # Send file
            if reply == "ready for transferring":
                while True:
                    # Read file with a buffer size
                    bytes_read = published_file.read(BUFFER_SIZE)
                    # If end of file
                    if not bytes_read:
                        break
                    # Sent to other client
                    self_connect.sendall(bytes_read)
            # Close all connections
            self_connect.close()
        else:
            print("File already in local repo")
        # Close file
        published_file.close()
    # Close socket
    server_connect.close()


def fetch(fname: str, scrap):
    # Initialize connection to server
    server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connect.connect((SERVER_HOST, SERVER_PORT))
    request = "fetch" + "*" + fname
    server_connect.send(request.encode())
    # Waiting for server to check file in local repo
    while True:
        check_local = server_connect.recv(1024).decode()
        if check_local:
            break
    if check_local == "File already in local repo":
        print(check_local)
    elif check_local == "File not recognize":
        print(check_local)
    else:
        target_client = check_local
        # Socket use for receive file from other client
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect((target_client, CLIENT_PORT))
        # file_receive = Thread(target=receive_file, args=(target_socket, fname))
        # file_receive.start()
        # Not use thread here bcs socket may close while thread is processing
        receive_file(target_socket, fname)
        # Close socket to target client
        target_socket.close()
    # Close socket to server
    server_connect.close()


def delete(fname: str, scrap):
    # Initialize connection to server
    server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connect.connect((SERVER_HOST, SERVER_PORT))
    request = "delete" + "*" + fname
    server_connect.send(request.encode())
    # Waiting for server to check file in local repo
    while True:
        check_local = server_connect.recv(1024).decode()
        if check_local:
            break
    # Print operation result
    print(check_local)
    # Close socket
    server_connect.close()


def discover(hostname: str, scrap):
    # Initialize connection to server
    server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connect.connect((SERVER_HOST, SERVER_PORT))
    request = "discover" + "*" + hostname
    server_connect.send(request.encode())
    # Waiting for server discover result
    while True:
        dis_result = server_connect.recv(1024).decode()
        if dis_result:
            break
    print(dis_result)


def list_client(scrap, filler):
    # Initialize connection to server
    server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connect.connect((SERVER_HOST, SERVER_PORT))
    request = "list"
    server_connect.send(request.encode())
    client_list = server_connect.recv(1024).decode().split("*")
    print(client_list)


def client_listening(host, port):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Linux client bind with "" host so don't need own host, Window client bind with its own host IP
    listening_socket.bind(("", port))
    listening_socket.listen(10)
    while True:
        client_conn, client_host = listening_socket.accept()
        # print(f"Accept connection from {client_host}")
        # print(CLIENT_HOST)
        if str(client_host[0]) == str(CLIENT_HOST):  # Self connect from publish command
            file_receive = Thread(target=receive_file, args=(client_conn, ""))
            file_receive.start()
        else:  # Connect from other clients
            # Receive fetch file from requested client
            reply = client_conn.recv(1024).decode()
            # Send file
            with open(reply, "rb") as fetched_file:
                while True:
                    # Read file with a buffer size
                    bytes_read = fetched_file.read(BUFFER_SIZE)
                    # If end of file
                    if not bytes_read:
                        break
                    # Sent to other client
                    client_conn.send(bytes_read)


if __name__ == "__main__":
    listening_thread = Thread(target=client_listening, args=(CLIENT_HOST, CLIENT_PORT))
    listening_thread.start()

    file_path = r"/home/ntdat/Downloads"
    file_name = "KGV_sisters.jpg"
    test_publish = Thread(target=publish, args=(file_path, file_name))
    test_publish.start()

    file_name = "First ending - Age of Stars.png"
    test_fetch = Thread(target=fetch, args=(file_name, 1))
    test_fetch.start()
