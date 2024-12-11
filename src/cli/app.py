import typer
from rich import print

app = typer.Typer()


def chat_interface():
    """
    A simple chat interface that runs in a loop.
    """
    print("[bold green]Welcome to the chat interface![/] Type 'exit' to quit.")
    while True:
        message = typer.prompt(typer.style("You", fg=typer.colors.BRIGHT_BLUE))
        if message.lower() == "exit":
            print("[bold red]Exiting chat. Goodbye![/]")
            break
        # Simulate receiving a response
        response = f"Echo: {message}"
        print(f"[bold magenta]Bot:[/] {response}")


@app.command()
def start_chat():
    """
    Start the chat interface.
    """
    chat_interface()


if __name__ == "__main__":
    app()
