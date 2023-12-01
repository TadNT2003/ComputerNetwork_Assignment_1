import socket
from threading import Thread

BUFFER_SIZE = 4096
SERVER_FULLNAME = socket.gethostbyname_ex(socket.gethostname())
SERVER_HOST = SERVER_FULLNAME[2][2]
SERVER_START_PORT = range(5000, 5010)  # Main port listens to clients' socket

def accept_connection(conn, addr):


def clients_listenning(host, port):
    listenning_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listenning_socket.bind((host, port))
    listenning_socket.listen(10)
    while True:
        conn, addr = listenning_socket.accept()


if __name__ == "__main__":
    for i in SERVER_START_PORT:
        sk_for_clients = Thread(target=clients_listenning, args=(SERVER_HOST, i))
        sk_for_clients.start()