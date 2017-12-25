from typing import List

from . import proto, soap


class Gateway:
    def __init__(self, control_url: str, ip: str) -> None:
        self.control_url = control_url
        self.ip = ip

    async def get_ext_ip(self) -> str:
        req = proto.RequestBuilder().ext_ip()
        resp = await soap.post(self.control_url, req.body(), req.header())
        return resp.xml().NewExternalIPAddress.string

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
            except (soap.InvalidArgsError, soap.InvalidArrayIndex):
                break

        return mappings

    async def get_port_mapping(self, i: int) -> proto.PortMapping:
        req = proto.RequestBuilder().get_port_mapping(i)
        resp = await self._make_request(req)
        return proto.parse_port_mapping(resp.body)

    async def add_port_mapping(self, mapping: proto.PortMapping) -> None:
        req = proto.RequestBuilder().add_port_mapping(mapping)
        await self._make_request(req)

    async def delete_port_mapping(self, ext_port: int, protocol: str) -> None:
        req = proto.RequestBuilder().delete_port_mapping(ext_port, protocol)
        await self._make_request(req)

    async def _make_request(self, req: proto.RequestBuilder) -> soap.Response:
        return await soap.post(self.control_url, req.body(), req.header())

    def __str__(self) -> str:
        return 'Gateway( control_url: "{}" )'.format(self.control_url)
