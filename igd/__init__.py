from typing import List

from . import proto, soap


class Gateway:
    def __init__(self, control_url: str) -> None:
        self.control_url = control_url

    async def get_ext_ip(self) -> str:
        soap_action, body = proto.get_ext_ip()
        resp = await soap.post(self.control_url, body, soap_action)
        return proto.parse_ext_ip(resp)

    # TODO: make it async, now every request is made synchronously
    # until all mappings are fetched. The reason is this issue:
    # https://github.com/dabeaz/curio/issues/236
    async def get_port_mappings(self) -> List[proto.PortMapping]:
        """Fetches all port mappings at once."""
        mappings = []
        i = 0
        while True:
            try:
                mappings.append(await self.get_port_mapping(i))
                i += 1
            except soap.Error as e:
                if e.code == 402:
                    break
                else:
                    raise e

        return mappings

    async def get_port_mapping(self, i: int) -> proto.PortMapping:
        soap_action, body = proto.get_port_mapping(i)
        resp = await soap.post(self.control_url, body, soap_action)
        return proto.parse_port_mapping(resp)

    async def add_port_mapping(self, mapping: proto.PortMapping) -> None:
        soap_action, req = proto.add_port_mapping(mapping)
        resp = await soap.post(self.control_url, req, soap_action)
        print(resp)

    def __str__(self) -> str:
        return 'Gateway( control_url: "{}" )'.format(self.control_url)
