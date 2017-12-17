from typing import Optional

import curio
import click

from . import core, proto


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
    curio.run(core.get_ip)


@click.command(
    short_help='Add new port mapping.',
    help='Adds new port mapping.',
)
@click.option('--ext-port', '-e', 'external_port', type=int, required=True,
              help='External port.',)
@click.option('--int-port', '-i', 'internal_port', type=int,
              help='Internal port. If unspecified, the same as --ext-port is '
                   'used.',)
@click.option('--ip', 'ip', type=str, required=False,
              help='Local IP that port will be forwarded to. If not '
                   'specified, this computer IP will be used.',)
@click.option('--protocol', '-p', 'protocol', type=str, default='TCP',
              show_default=True,
              help='UDP or TCP. Mixed letter case allowed.',)
@click.option('--description', '-t', 'description', type=str, default='pyigd',
              show_default=True,
              help='Port mapping description.',)
@click.option('--duration', '-d', 'duration', type=int, default=0,
              show_default=True,
              help='Port mapping duration. If unspecified, mapping stays '
              'until IGD/router reboot.',)
def add(external_port: int, internal_port: Optional[int], ip: Optional[str],
        protocol: str,
        description: str, duration: int):
    internal_port = internal_port or external_port
    mapping = proto.PortMapping(
        '', internal_port, external_port, protocol, ip, True, description,
        duration)
    curio.run(core.add_port_mapping, mapping)


@click.command(
    short_help='Remove port mapping.',
    help='Removes port mapping that matches given filters. If protocol is '
         'not specified, mappings for both UDP and TCP are removed.',
)
@click.option('--protocol', '-p', 'protocol', type=str,
              help='If not specified, all mappings matching given pattern '
                   'are removed. Otherwise, only the mappings with given '
                   'protcol are removed: UDP or TCP. Mixed letter case '
                   'allowed.',)
@click.argument('pattern', type=str, required=True,)
def rm(pattern: str, protocol: Optional[str]):
    curio.run(core.delete_port_mappings, pattern, protocol)


@click.group()
def cli():
    pass


def main() -> None:
    cli.add_command(ls)
    cli.add_command(ip)
    cli.add_command(add)
    cli.add_command(rm)
    cli()


if __name__ == '__main__':
    main()
