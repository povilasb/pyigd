from typing import List

from tabulate import tabulate
from curio import socket

from . import ssdp, proto


async def get_ip() -> None:
    gateway = await ssdp.find_gateway()
    return await gateway.get_ext_ip()


async def get_port_mappings() -> List[proto.PortMapping]:
    gateway = await ssdp.find_gateway()
    mappings = await gateway.get_port_mappings()
    return _format_mappings(mappings)


async def add_port_mapping(mapping: proto.PortMapping) -> None:
    gateway = await ssdp.find_gateway()
    if mapping.ip is None:
        mapping.ip = await _get_local_ip_to(gateway.ip)
    await gateway.add_port_mapping(mapping)


async def delete_port_mapping(ext_port: int, protocol: str) -> None:
    gateway = await ssdp.find_gateway()
    await gateway.delete_port_mapping(ext_port, protocol)


def _format_mappings(mappings: List[proto.PortMapping]) -> str:
    headers = ['Description', 'External Port', 'Protocol', 'Internal Port',
               'IP', 'Status']
    mappings = [_port_mapping_to_arr(m) for m in mappings]
    return tabulate(mappings, headers=headers)


def _port_mapping_to_arr(mapping: proto.PortMapping) -> list:
    status = 'Enabled' if mapping.enabled else 'Disabled'
    return [mapping.description, mapping.external_port, mapping.protocol,
            mapping.internal_port, mapping.ip, status]


async def _get_local_ip_to(gateway_ip: str) -> str:
    """Find IP address of current interface."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    await sock.connect((gateway_ip, 0))
    return sock.getsockname()[0]
