from hamcrest import assert_that, is_

from igd import proto


def describe_parse_port_mapping():
    def it_extracts_fields_from_xml_response():
        xml_resp = b"""
        <?xml version="1.0"?>
        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <SOAP-ENV:Body>
                <u:GetGenericPortMappingEntryResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
                    <NewRemoteHost>host1</NewRemoteHost>
                    <NewExternalPort>40460</NewExternalPort>
                    <NewProtocol>TCP</NewProtocol>
                    <NewInternalPort>44837</NewInternalPort>
                    <NewInternalClient>192.168.1.2</NewInternalClient>
                    <NewEnabled>1</NewEnabled>
                    <NewPortMappingDescription>pyigd</NewPortMappingDescription>
                    <NewLeaseDuration>100</NewLeaseDuration>
                </u:GetGenericPortMappingEntryResponse>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """

        port_mapping = proto.parse_port_mapping(xml_resp)

        assert_that(port_mapping.external_port, is_(40460))
        assert_that(port_mapping.internal_port, is_(44837))
        assert_that(port_mapping.ip, is_('192.168.1.2'))
        assert_that(port_mapping.protocol, is_('TCP'))
        assert_that(port_mapping.remote_host, is_('host1'))
        assert_that(port_mapping.enabled, is_(True))
        assert_that(port_mapping.description, is_('pyigd'))
        assert_that(port_mapping.duration, is_(100))


def describe_parse_ext_ip():
    def it_extracts_external_ip_from_xml_response():
        xml_resp = b"""
        <?xml version="1.0"?>
        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <SOAP-ENV:Body>
                <u:GetExternalIPAddressResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
                    <NewExternalIPAddress>1.2.3.4</NewExternalIPAddress>
                </u:GetExternalIPAddressResponse>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """

        ext_ip = proto.parse_ext_ip(xml_resp)

        assert_that(ext_ip, is_('1.2.3.4'))
