from __future__ import annotations

import os
from typing import Any

import rich
import typer
import yaml


def _make_plots(
    input_files: list[str],
    config_file: str,
    output_dir: str,
    force: bool,
) -> None:
    from fast_plotter.v1 import make_plots

    if not os.path.exists(config_file):
        rich.print(f"[red]Config file {config_file} does not exist[/]")
        raise typer.Exit(1)
    for input_file in input_files:
        if not os.path.exists(input_file):
            rich.print(f"[red]Input file {input_file} does not exist[/]")
            return
    if os.path.exists(output_dir) and not force:
        rich.print(
            f"[red]Output directory {output_dir} already exists. Use --force to overwrite.[/]",
        )
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # convert YAML config file to dict
    with open(config_file) as fp:
        plot_config: dict[str, Any] = yaml.safe_load(fp)

    make_plots(plot_config, input_files, output_dir)
