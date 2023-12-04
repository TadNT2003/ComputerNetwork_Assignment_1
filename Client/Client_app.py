import typer, socket, Client_for_Linux, Client

app = typer.Typer()
SERVER_HOST = Client.SERVER_HOST
SERVER_APP_PORT = Client.SERVER_APP_PORT
CLIENT_HOST = Client.CLIENT_HOST
CLIENT_COMMAND_PORT = Client.CLIENT_COMMAND_PORT
client_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@app.command()
def publish(lname: str, fname: str):
    """Publish file from client's system to it local repo and inform the server"""
    try:
        # Try to connect to client program every command
        client_connect.connect((CLIENT_HOST, CLIENT_COMMAND_PORT))
    except ConnectionError:
        print("Connection Error! Client has not been up yet")
    else:
        command = "publish" + "*" + lname + "*" + fname
        client_connect.send(command.encode())
        command_output = client_connect.recv(1024).decode()
        print(command_output)
        # Close socket
        client_connect.close()


@app.command()
def fetch(fname: str):
    """Fetch a file from a target client"""
    try:
        # Try to connect to client program every command
        client_connect.connect((CLIENT_HOST, CLIENT_COMMAND_PORT))
    except ConnectionError:
        print("Connection Error! Client has not been up yet")
    else:
        command = "fetch" + "*" + fname
        client_connect.send(command.encode())
        command_output = client_connect.recv(1024).decode()
        print(command_output)
        # Close socket
        client_connect.close()


@app.command()
def delete(fname: str):
    """Delete file from client local repo in server database"""
    try:
        # Try to connect to client program every command
        client_connect.connect((CLIENT_HOST, CLIENT_COMMAND_PORT))
    except ConnectionError:
        print("Connection Error! Client has not been up yet")
    else:
        command = "delete" + "*" + fname
        client_connect.send(command.encode())
        command_output = client_connect.recv(1024).decode()
        print(command_output)
        # Close socket
        client_connect.close()


@app.command()
def discover(hostname: str):
    """Print the list of published file from a client"""
    try:
        # Try to connect to client program every command
        client_connect.connect((CLIENT_HOST, CLIENT_COMMAND_PORT))
    except ConnectionError:
        print("Connection Error! Client has not been up yet")
    else:
        command = "discover" + "*" + hostname
        client_connect.send(command.encode())
        command_output = client_connect.recv(1024).decode()
        print(command_output)
        # Close socket
        client_connect.close()


@app.command()
def list():
    """Print the list all clients that have connected to server"""
    try:
        # Try to connect to client program every command
        client_connect.connect((CLIENT_HOST, CLIENT_COMMAND_PORT))
    except ConnectionError:
        print("Connection Error! Client has not been up yet")
    else:
        command = "list"
        client_connect.send(command.encode())
        command_output = client_connect.recv(1024).decode()
        print(command_output)
        # Close socket
        client_connect.close()


@app.callback()
def callback():
    """Welcome! This is the CLI for the Client of Assignment 1 file-sharing app"""


if __name__ == "__main__":
    # Get IP address for Linux client, at this time Client.py have not connected to server yet
    server_connect = socket.socket()
    server_connect.connect((SERVER_HOST, SERVER_APP_PORT))
    # To find true IP use for connection
    CLIENT_HOST = server_connect.getsockname()[0]
    server_connect.send(CLIENT_HOST.encode())
    # print(CLIENT_HOST)
    server_connect.close()
    # Launch CLI app
    app()