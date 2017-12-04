import curio
import click

from . import ssdp, proto, soap, core


@click.command(
    short_help='Get all port mappings.',
    help='Get all port mappings. Various filtering options available.',
)
def ls():
    port_mapping = curio.run(core.get_port_mappings)
    print(port_mapping)


@click.command(
    short_help='Get external IP from IGD.',
    help='Finds Internet Gateway Device and queries for externl IP.',
)
def ip():
    ext_ip = curio.run(core.get_ip)
    print(ext_ip)


@click.group()
def cli():
    pass


def main() -> None:
    cli.add_command(ls)
    cli.add_command(ip)
    cli()


if __name__ == '__main__':
    main()
