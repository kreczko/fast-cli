from __future__ import annotations

import rich
import typer

# from .logger import console_handler, user_logger
from . import __version__
from ._download import download_from_json
from ._software import _find_fast_hep_packages

app = typer.Typer()


@app.command()
def version() -> None:
    """
    Show version
    """
    rich.print(f"[blue]FAST-HEP CLI Version[/]: [magenta]{__version__}[/]")


@app.command()
def versions() -> None:
    """Show versions of all found FAST-HEP packages"""
    for package, version in _find_fast_hep_packages():
        rich.print(f"[blue]{package}[/]: [magenta]{version}[/]")


@app.command()
def download(
    json_input: str = typer.Option(None, "--json", "-j", help="JSON input file"),
    destination: str = typer.Option(
        None, "--destination", "-d", help="Destination directory"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force download; overwriting existing files"
    ),
) -> None:
    """Download files specified in JSON input file into destination directory"""
    download_from_json(json_input, destination, force)


def main() -> typer.Typer:
    return app()
