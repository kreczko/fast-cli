""" Entry point for fasthep command line interface """
from __future__ import annotations

from enum import Enum

import rich
import typer
from tabulate import tabulate

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


class DisplayFormats(str, Enum):
    """Display formats for command output"""

    SIMPLE = "simple"
    PIP = "pip"
    TABLE = "table"


@app.command()
def versions(
    display_format: DisplayFormats = typer.Option(
        "simple", "--display", "-d", help="Display format"
    )
) -> None:
    """Show versions of all found FAST-HEP packages"""
    separator = ": "
    if display_format == DisplayFormats.PIP:
        separator = "=="

    if display_format in (DisplayFormats.SIMPLE, DisplayFormats.PIP):
        for package, _version in _find_fast_hep_packages():
            rich.print(f"[blue]{package}[/]{separator}[magenta]{_version}[/]")
    elif display_format == DisplayFormats.TABLE:
        headers = ["Package", "Version"]
        table = list(_find_fast_hep_packages())
        tablefmt = "github"
        rich.print(
            tabulate(
                table,
                headers=headers,
                tablefmt=tablefmt,
                colalign=("left", "right"),
            )
        )


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
    """Download files specified in JSON input file into destination directory.
    JSON input file should be a dictionary with the following structure:
    {   "file1": "url1", "file2": "url2", ... }
    """
    download_from_json(json_input, destination, force)


@app.command()
def carpenter(
    dataset_cfg: str = typer.Argument(None, help="Dataset config to run over"),
    sequence_cfg: str = typer.Argument(None, help="Config for how to process dataset"),
    output_dir: str = typer.Option(
        "output", "--outdir", "-o", help="Where to save the results"
    ),
    processing_backend: str = typer.Option(
        "multiprocessing", "--backend", "-b", help="Backend to use for processing"
    ),
    store_bookkeeping: bool = typer.Option(
        True, "--store-bookkeeping", "-s", help="Store bookkeeping information"
    ),
) -> None:
    """
    Run the FAST-HEP carpenter
    """
    try:
        import fast_curator
        import fast_flow.v1
        from fast_carpenter import backends, bookkeeping, data_import
    except ImportError:
        rich.print(
            "[red]FAST-HEP carpenter is not installed. Please run 'pip install fast-carpenter'[/]",
        )
        return
    import os
    import sys

    from ._carpenter import CarpenterSettings

    sequence, sequence_cfg = fast_flow.v1.read_sequence_yaml(
        sequence_cfg,
        output_dir=output_dir,
        backend="fast_carpenter",
        return_cfg=True,
    )
    datasets = fast_curator.read.from_yaml(dataset_cfg)
    backend = backends.get_backend(processing_backend)
    if store_bookkeeping:
        book_keeping_file = os.path.join(output_dir, "book-keeping.tar.gz")
        bookkeeping.write_booking(
            book_keeping_file, sequence_cfg, datasets, cmd_line_args=sys.argv[1:]
        )
        # fast_carpenter.store_bookkeeping(datasets, output_dir)
    settings = CarpenterSettings(
        ncores=1,
        outdir=output_dir,
    )
    results, _ = backend.execute(
        sequence,
        datasets,
        args=settings,
        plugins={
            "data_import": data_import.get_data_import_plugin("multitree", dataset_cfg)
        },
    )
    rich.print(f"[blue]Results[/]: {results}")
    rich.print(f"[blue]Output written to directory {output_dir}[/]")


@app.command()
def plotter(
    input_files: list[str] = typer.Argument(None, min=1, help="Input files"),
    config_file: str = typer.Option(None, "--config", "-c", help="PlotConfig file"),
    output_dir: str = typer.Option(
        "output", "--outdir", "-o", help="Where to save the results"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing output_dir"
    ),
) -> None:
    """Command to invoke the FAST-HEP plotter"""
    from ._plotter import _make_plots

    _make_plots(input_files, config_file, output_dir, force)


def main() -> typer.Typer:
    """Entry point for fasthep command line interface"""
    return app()
