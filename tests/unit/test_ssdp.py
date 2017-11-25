from hamcrest import assert_that, is_

from igd import ssdp


def read_fixture_bytes(fixture_name: str) -> bytes:
    with open('tests/fixtures/{}'.format(fixture_name), 'rb') as f:
        return f.read()


def describe_parse_igd_profile():
    def it_():
        resp_xml = read_fixture_bytes('igd_info_resp.xml')

        control_url, upnp_schema = ssdp._parse_igd_profile(resp_xml)

        assert_that(control_url, is_('/ipc'))
        assert_that(upnp_schema, is_('WANIPConnection'))
