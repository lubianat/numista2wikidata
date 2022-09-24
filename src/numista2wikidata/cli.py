import click

from numista2wikidata import get_coin_info, get_missing_coin_info


@click.group()
def cli():
    """Connecting Numista info to Wikidata on-demand."""


cli.add_command(get_coin_info.main)
cli.add_command(get_missing_coin_info.main)

if __name__ == "__main__":
    cli()
