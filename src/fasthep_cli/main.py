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
    simple = "simple"
    pip = "pip"
    table = "table"


@app.command()
def versions(
    display_format: DisplayFormats = typer.Option(
        "simple", "--display", "-d", help="Display format"
    )
) -> None:
    """Show versions of all found FAST-HEP packages"""
    separator = ": "
    if display_format == DisplayFormats.pip:
        separator = "=="

    if display_format == DisplayFormats.simple or display_format == DisplayFormats.pip:
        for package, version in _find_fast_hep_packages():
            rich.print(f"[blue]{package}[/]{separator}[magenta]{version}[/]")
    elif display_format == DisplayFormats.table:
        headers = ["Package", "Version"]
        table = [(package, version) for package, version in _find_fast_hep_packages()]
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
    """Download files specified in JSON input file into destination directory"""
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
            style="red",
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


def main() -> typer.Typer:
    return app()
