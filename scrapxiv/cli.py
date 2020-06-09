import click

from scrapxiv.shelf import Shelf
from scrapxiv import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """A collection of commands for running scrapxiv locally."""
    pass


@cli.command()
@click.option(
    "--key-words",
    "--keywords",
    "-k",
    "keywords",
    required=True,
    type=str,
    default=None,
    help="Keywords for the specific query.",
)
@click.option(
    "--output-file",
    "--output",
    "-o",
    "output_file",
    required=True,
    type=str,
    default=None,
    help="path to where the .csv will be saved.",
)
@click.option(
    "--max",
    "-m",
    "max_",
    required=True,
    type=int,
    help="Max number of queried papers.",
)
@click.option(
    "--start",
    "-s",
    "start",
    required=True,
    type=int,
    default=None,
    help="queried papers to skip before saving them.",
)
@click.option(
    '--emails', 
    '-e',
    "emails",
    is_flag=True, 
    default=False,
    help="Retrive the emails (this would parse the papers getting the info needed)."
)
def authors(keywords, output_file, max_, start, emails):
    """Arxiv web scraper - based on the Arxiv API."""
    shelf = Shelf()
    shelf.query(keywords=keywords, start_index=start, max_results=max_)
    df = shelf.get_authors_dataframe(get_emails=emails)
    df.to_csv(output_file)
