import click
import sys
import os
from centaur import app


@click.command()
@click.version_option()
@click.option('--config', default=None,
              help='Config file to use; default is ~/.centaurrc.')
def main(config):
    """Parse a number of RSS or Atom feeds, apply optional filters,
    and generate a single combined feed as output."""
    if config is None:
        config = os.path.expanduser('~/.centaurrc')
    if not os.path.isfile(config):
        bail("Unable to open {}".format(config))
    try:
        with open(config, "rb") as f:
            parsed_config = app.parse_config(f)
            if parsed_config is False:
                click.echo("Unable to parse {}".format(config))
                sys.exit(1)
    except IOError as e:
        bail("Unable to open {}".format(config))
    try:
        g = app.build_graph(parsed_config)
        app.run_graph(g)
    except ValueError as e:
        bail("{}".format(e))
    sys.exit(0)


def bail(message):
    click.echo(message)
    sys.exit(1)
