import click
import shutil
import sys
from pathlib import Path
from src.client.client import Client

def setup(path: Path):
    directory = path / ".shh"
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        template = Path(__file__).parent / "templates" / "userdata.json"
        if template.exists():
            shutil.copy(template, directory / "userdata.json")
            return True
    return False

@click.group(name="shh", context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    pass

@cli.command(help="Show info about shh.")
def about():
    click.echo("shh - Private Chat for Developers (0.1.0)")

@cli.command(help="Initialize environment.")
@click.argument('path', type=click.Path(path_type=Path), default=".")
def create(path):
    directory = path.absolute()
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    if setup(directory):
        click.echo(f"Initialized: {directory}/.shh")
    else:
        click.echo(f"Exists: {directory}/.shh")

@cli.command(help="Start client.")
@click.argument('path', type=click.Path(exists=True, path_type=Path), default=".")
def start(path):
    directory = path.absolute()
    if not (directory / ".shh").exists():
        click.echo(f"Error: .shh not found in {directory}")
        return
    Client(directory).run()

if __name__ == "__main__":
    try:
        cli(prog_name="shh", standalone_mode=False)
    except click.ClickException as e:
        click.echo(f"Error: {e.format_message()}")
        sys.exit(1)