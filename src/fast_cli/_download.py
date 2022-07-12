from __future__ import annotations

import json
import os

import requests
import typer


def download_from_url(url: str, destination: str, force: bool = False) -> None:
    if os.path.exists(path=destination) and not force:
        typer.echo(f"{destination} already exists, skipping...")
        return
    r = requests.get(url, allow_redirects=True)
    with open(destination, "wb") as f:
        f.write(r.content)


def download_from_json(json_input: str, destination: str, force: bool = False) -> None:
    with open(json_input) as json_file:
        data = json.load(json_file)
    if not os.path.exists(destination):
        os.makedirs(destination)
    for name, url in data.items():
        # TODO: this should be a logger
        typer.echo(f"Downloading {name}...")
        output_path = os.path.join(destination, name)
        download_from_url(url, output_path)
