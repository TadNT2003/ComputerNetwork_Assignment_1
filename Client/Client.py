import os.path
import socket
from threading import Thread

BUFFER_SIZE = 4096
SERVER_HOST = "10.1.70.129"
SERVER_PORT = 5000

if __name__ == "__main__":
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect((SERVER_HOST, SERVER_PORT))
    filename = "picture.jpg"
    filesize = os.path.getsize(filename)
    socket.send(f"{filename}_{filesize}".encode())
    reply = socket.recv(1024).decode()
    if reply == "ready for transferring":
        with open("picture.jpg", "rb") as send_file:
            while True:
                # Read file with a buffer size
                bytes_read = send_file.read(BUFFER_SIZE)
                # If end of file
                if not bytes_read:
                    break
                # Already in binary so no need to encode
                socket.sendall(bytes_read)
    socket.close()