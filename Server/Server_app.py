import typer, socket, Server

app = typer.Typer()
SERVER_HOST = Server.SERVER_HOST
SERVER_COMMAND_PORT = Server.SERVER_COMMAND_PORT
server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@app.command()
def discover(hostname: str):
    """Print the list of published file from a client"""
    try:
        # Try to connect to server program every command
        server_connect.connect((SERVER_HOST, SERVER_COMMAND_PORT))
    except ConnectionError:
        print("Connection Error! Server has not been up yet")
    else:
        command = "discover" + "*" + hostname
        server_connect.send(command.encode())
        command_output = server_connect.recv(1024).decode()
        print(command_output)
        # Close socket
        server_connect.close()


@app.callback()
def callback():
    """Welcome! This is the CLI for the Server of Assignment 1 file-sharing app"""


if __name__ == "__main__":
    app()