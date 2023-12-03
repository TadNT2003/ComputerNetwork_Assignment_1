import typer, socket
from threading import Thread

app = typer.Typer()
SERVER_FULLHOST = socket.gethostbyname_ex(socket.gethostname())
SERVER_HOST = SERVER_FULLHOST[2][2]
SERVER_PORT = 5000
SERVER_COMMAND_PORT = 10000
server_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@app.command()
def main():
    """This is the CLI for the Server"""
    print("This is the CLI for the Server. Add help option for more information")


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


if __name__ == "__main__":
    app()