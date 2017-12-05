from typing import List

from tabulate import tabulate

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
    await gateway.add_port_mapping(mapping)


def _format_mappings(mappings: List[proto.PortMapping]) -> str:
    headers = ['Description', 'External Port', 'Protocol', 'Internal Port',
               'IP', 'Status']
    mappings = [_port_mapping_to_arr(m) for m in mappings]
    return tabulate(mappings, headers=headers)


def _port_mapping_to_arr(mapping: proto.PortMapping) -> list:
    status = 'Enabled' if mapping.enabled else 'Disabled'
    return [mapping.description, mapping.external_port, mapping.protocol,
            mapping.internal_port, mapping.ip, status]
