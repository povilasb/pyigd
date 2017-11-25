from . import proto, soap


class Gateway:
    def __init__(self, control_url: str) -> None:
        self.control_url = control_url

    async def get_ext_ip(self) -> str:
        soap_action, body = proto.get_ext_ip()
        resp = await soap.post(self.control_url, body, soap_action)
        return proto.parse_ext_ip(resp)

    async def get_port_mapping(self, i: int) -> proto.PortMapping:
        soap_action, body = proto.get_port_mapping(i)
        resp = await soap.post(self.control_url, body, soap_action)
        return proto.parse_port_mapping(resp)

    def __str__(self) -> str:
        return 'Gateway( control_url: "{}" )'.format(self.control_url)
