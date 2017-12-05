from unittest.mock import patch, MagicMock

from hamcrest import assert_that, is_
import curio
from aiomock import AIOMock

from igd import ssdp


def read_fixture_bytes(fixture_name: str) -> bytes:
    with open('tests/fixtures/{}'.format(fixture_name), 'rb') as f:
        return f.read()


def describe_parse_igd_profile():
    def it_extracts_upnpn_scheme_and_control_url():
        resp_xml = read_fixture_bytes('igd_info_resp.xml')

        control_url, upnp_schema = ssdp._parse_igd_profile(resp_xml)

        assert_that(control_url, is_('/ipc'))
        assert_that(upnp_schema, is_('WANIPConnection'))


def describe_make_ssdp_request():
    def it_returns_ip_from_which_the_response_was_received():
        sock = AsyncMock()
        resp = b'HTTP/1.1 200 OK\r\nLOCATION: http://192.168.0.1:1900/igd.xml\r\n'
        sock.recvfrom.async_return_value = (resp, ('192.168.0.1', 1900))
        with patch('curio.socket.socket', MagicMock(return_value=sock)):
            _, igd_ip = curio.run(ssdp._make_ssdp_request())

            assert_that(igd_ip, is_('192.168.0.1'))


class AsyncMock(AIOMock):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.async_return_value = kwargs.get('async_return_value')
