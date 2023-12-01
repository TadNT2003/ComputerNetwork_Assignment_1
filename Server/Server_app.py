import typer

app = typer.Typer()

@app.command()
def main():
    print("Hello world")
    while True:
        print("_")

if __name__ == "__main__":
    app()