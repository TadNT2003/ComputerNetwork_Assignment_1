import socket
from threading import Thread

BUFFER_SIZE = 4096
SERVER_FULLHOST = socket.gethostbyname_ex(socket.gethostname())
SERVER_HOST = SERVER_FULLHOST[2][2]
SERVER_PORT = 5000

# Receive file process
def receive_file(conn, host):
    file_info = conn.recv(1024).decode()
    filename, filesize = file_info.split("_")
    reply = "ready for transferring"
    conn.send(reply.encode())
    with open("receive_picture.jpg", "wb") as received_file:
        while True:
            # Receive file from client
            bytes_read = conn.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            received_file.write(bytes_read)


# Listen to client on server's socket
def client_listening(host, port):
    listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_socket.bind((host, port))
    listening_socket.listen(10)
    while True:
        client_conn, client_host = listening_socket.accept()
        print(f"Accept connection from {client_host}")
        file_received = Thread(target=receive_file, args=(client_conn, client_host))
        file_received.start()

if __name__ == "__main__":
    # print(SERVER_FULLHOST)
    Main_Socket = Thread(target=client_listening, args=(SERVER_HOST, SERVER_PORT))
    Main_Socket.start()