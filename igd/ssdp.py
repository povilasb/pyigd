"""SSDP utils to locate Internet Gateway Device."""

import re
from typing import Tuple, List

from curio import socket
import asks
from yarl import URL
from bs4 import BeautifulSoup

from . import proto, soap


asks.init('curio')

SSDP_REQUEST = b'M-SEARCH * HTTP/1.1\r\n' \
    b'HOST: 239.255.255.250:1900\r\n' \
    b'MAN: "ssdp:discover"\r\n' \
    b'MX: 2\r\n' \
    b'ST: urn:schemas-upnp-org:device:InternetGatewayDevice:1\r\n'\
    b'\r\n'


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


async def find_gateway() -> Gateway:
    location, gateway_ip = await _make_ssdp_request()
    resp = await asks.get(location)
    control_path, upnp_schema = _parse_igd_profile(resp.content)
    control_url = URL(location).with_path(control_path)
    return Gateway(str(control_url), gateway_ip)


async def _make_ssdp_request() -> Tuple[str, str]:
    """Broadcast a UDP SSDP M-SEARCH packet and return IGD location.

    Returns:
        URL to IGD info and IGD IP address.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    await sock.sendto(SSDP_REQUEST, ('239.255.255.250', 1900))
    # TODO: add timeout
    resp, addr = await sock.recvfrom(4096)
    return _parse_location_from(resp.decode('ascii')), addr[0]


# TODO: return multiple locations
def _parse_location_from(response: str) -> str:
    """Parse raw HTTP response to retrieve the UPnP location header."""
    parsed = re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', response)
    location_header = list(
        filter(lambda x: x[0].lower() == 'location', parsed))

    if not len(location_header):
        raise Exception('location header not present')
    return location_header[0][1]


def _parse_igd_profile(profile_xml: bytes) -> Tuple[str, str]:
    """
    Traverse the profile xml DOM looking for either WANIPConnection or
    WANPPPConnection and return the value found as well as the 'controlURL'.
    """
    doc = BeautifulSoup(profile_xml, 'lxml-xml')
    elems = doc.find_all('serviceType')
    for service_type in elems:
        upnp_schema = service_type.string.split(':')[-2]
        if upnp_schema in ['WANIPConnection', 'WANPPPConnection',
                           'WFAWLANConfig']:
            control_url = service_type.parent.find('controlURL').string
            return control_url, upnp_schema

    raise Exception('No IGD data found in response')
