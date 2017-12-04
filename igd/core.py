from typing import List

from . import ssdp, proto


async def get_ip() -> None:
    gateway = await ssdp.find_gateway()
    return await gateway.get_ext_ip()


async def get_port_mappings() -> List[proto.PortMapping]:
    gateway = await ssdp.find_gateway()
    return await gateway.get_port_mappings()
