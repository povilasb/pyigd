from . import ssdp

async def get_ip() -> None:
    gateway = await ssdp.find_gateway()
    return await gateway.get_ext_ip()
