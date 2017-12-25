from typing import List, Optional, Callable, Any

from tabulate import tabulate
from curio import socket
import curio

from . import ssdp, proto, soap, Gateway


def handle_exceptions(func: Callable) -> Callable[..., Any]:
    """Helper function to reduce boilerplate to handle expected exceptions.

    Works with async functions only.
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except soap.HttpError as e:
            print('Unexpected HTTP error: {} {}'.format(e.code, e.message))
        except soap.InvalidArgsError as e:
            print('Invalid SOAP argument: {}'.format(e.message))
    return wrapper


@handle_exceptions
async def get_ip() -> None:
    gateway = await ssdp.find_gateway()
    ip = await gateway.get_ext_ip()
    print(ip)


async def get_port_mappings() -> str:
    gateway = await ssdp.find_gateway()
    mappings = await gateway.get_port_mappings()
    return _format_mappings(mappings)


@handle_exceptions
async def add_port_mapping(mapping: proto.PortMapping) -> None:
    gateway = await ssdp.find_gateway()
    if mapping.ip is None:
        mapping.ip = await _get_local_ip_to(gateway.ip)
    await gateway.add_port_mapping(mapping)


# TODO: return how many ports were removed
@handle_exceptions
async def delete_port_mappings(pattern: str, protocol: Optional[str]) -> None:
    """Deletes port mappings by given pattern."""
    gateway = await ssdp.find_gateway()
    protocols = [protocol.upper()] if protocol is not None else ['TCP', 'UDP']
    if pattern.isdigit():
        await _delete_port_mappings_by_port(gateway, int(pattern), protocols)
    else:
        await _delete_port_mappings_by_description(gateway, pattern, protocols)


async def _delete_port_mappings_by_port(gateway: Gateway, ext_port: int,
                                        protocols: List[str]) -> None:
    for prot in protocols:
        try:
            await gateway.delete_port_mapping(ext_port, prot)
        except (soap.InvalidArgsError, soap.NoSuchEntryInArray):
            pass


async def _delete_port_mappings_by_description(gateway: Gateway, pattern: str,
                                               protocols: List[str]) -> None:
    mappings = await gateway.get_port_mappings()
    mappings = [m for m in mappings if m.description == pattern and
                m.protocol in protocols]
    tasks = [await curio.spawn(gateway.delete_port_mapping,
                               m.external_port, m.protocol) for m in mappings]
    for t in tasks:
        # TODO: add timeout
        await t.join()


def _format_mappings(mappings: List[proto.PortMapping]) -> str:
    headers = ['Description', 'External Port', 'Protocol', 'Internal Port',
               'IP', 'Status']
    rows = [_port_mapping_to_arr(m) for m in mappings]
    return tabulate(rows, headers=headers)


def _port_mapping_to_arr(mapping: proto.PortMapping) -> List[str]:
    status = 'Enabled' if mapping.enabled else 'Disabled'
    return [mapping.description, str(mapping.external_port), mapping.protocol,
            str(mapping.internal_port), mapping.ip, status]


async def _get_local_ip_to(gateway_ip: str) -> str:
    """Find IP address of current interface."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    await sock.connect((gateway_ip, 0))
    return sock.getsockname()[0]
