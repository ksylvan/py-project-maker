"""Main module for the pyhatchery package."""

import click

from pyhatchery import __version__


def main():
    """Main function to execute the script."""
    click.echo(f"Hello from pyhatchery! Version {__version__}.")


if __name__ == "__main__":
    main()
