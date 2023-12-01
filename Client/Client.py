import os
import socket
from threading import Thread

BUFFER_SIZE = 4096
SERVER_HOST = "192.168.31.48"
SERVER_PORT = 5000
CLIENT_HOST = socket.gethostname()
CLIENT_PORT = range(15000, 15010)
CURRENT_USE_PORT = 15000

def receive_file(conn, host):
    file_info = conn.recv(1024).decode()
    # print(file_info)
    filename, filesize = file_info.split("*")
    # filesize = file_info[1]
    reply = "ready for transferring"
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
    global published_file
    server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connect.connect((SERVER_HOST, SERVER_PORT))
    full_filename = lname + "\\" + fname
    print(full_filename)
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
        if check_local == "Continue":
            # Add file from system file to local repo
            # Connect to itself to transfer file from file system to local repo
            self_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self_connect.connect((CLIENT_HOST, CURRENT_USE_PORT))
            filesize = os.path.getsize(full_filename)
            self_connect.send(f"{fname}*{filesize}".encode())
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
            print(check_local)
    finally:
        published_file.close()
        server_connect.close()

def client_listening(host, port):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind((host, port))
    listening_socket.listen(10)
    connection_accepted = False
    while True:
        client_conn, client_host = listening_socket.accept()
        # print(f"Accept connection from {client_host}")
        file_receive = Thread(target=receive_file, args=(client_conn, client_host))
        file_receive.start()

if __name__ == "__main__":
    for i in CLIENT_PORT:
        main_socket = Thread(target=client_listening, args=(CLIENT_HOST, i))
        main_socket.start()

    file_path = r"C:\Users\Admin\OneDrive\Pictures\Elden Ring"
    file_name = "First ending - Age of Stars.png"
    test_publish = Thread(target=publish, args=(file_path, file_name))
    test_publish.start()