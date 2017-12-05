"""SSDP utils to locate Internet Gateway Device."""

import re
from typing import Tuple

from curio import socket
import asks
from yarl import URL
from bs4 import BeautifulSoup

from . import Gateway


asks.init('curio')

SSDP_REQUEST = b'M-SEARCH * HTTP/1.1\r\n' \
    b'HOST: 239.255.255.250:1900\r\n' \
    b'MAN: "ssdp:discover"\r\n' \
    b'MX: 2\r\n' \
    b'ST: urn:schemas-upnp-org:device:InternetGatewayDevice:1\r\n'\
    b'\r\n'


async def find_gateway() -> Gateway:
    location = await _make_ssdp_request()
    resp = await asks.get(location)
    control_path, upnp_schema = _parse_igd_profile(resp.content)
    control_url = URL(location).with_path(control_path)
    return Gateway(str(control_url))


async def _make_ssdp_request() -> str:
    """Broadcast a UDP SSDP M-SEARCH packet and return IGD location."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    await sock.sendto(SSDP_REQUEST, ('239.255.255.250', 1900))
    # TODO: add timeout
    resp = await sock.recv(4096)
    return _parse_location_from(resp.decode('ascii'))


# TODO: return multiple locations
def _parse_location_from(response: str) -> str:
    """Parse raw HTTP response to retrieve the UPnP location header."""
    parsed = re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', response)
    location_header = list(
        filter(lambda x: x[0].lower() == 'location', parsed))

    if not len(location_header):
        return False
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


# TODO: use gateway address to discover my IP. Because for every gateway
# there's different IP
async def _get_local_ip() -> str:
    """ Find IP address of current interface."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # not using <broadcast> because gevents getaddrinfo doesn't like that
    # using port 1 as per hobbldygoop's comment about port 0 not working on osx:
    # https://github.com/sirMackk/ZeroNet/commit/fdcd15cf8df0008a2070647d4d28ffedb503fba2#commitcomment-9863928
    await sock.connect(('239.255.255.250', 1))
    return sock.getsockname()[0]
