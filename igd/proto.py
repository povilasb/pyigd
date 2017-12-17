from bs4 import BeautifulSoup


class PortMapping:
    def __init__(self, remote_host: str, external_port: int,
                 internal_port: int, protocol: str, ip: str, enabled: bool,
                 description: str, duration: int) -> None:
        self.remote_host = remote_host
        self.external_port = external_port
        self.internal_port = internal_port
        self.protocol = protocol
        self.ip = ip
        self.enabled = enabled
        self.description = description
        self.duration = duration

    def __str__(self) -> str:
        return 'PortMapping {}'.format(str(self.__dict__))

    def __repr__(self) -> str:
        return str(self)


class RequestBuilder:
    def __init__(self) -> None:
        self._body_tmpl = """
<?xml version="1.0"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
        xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" >
    <s:Body>
        {}
    </s:Body>
</s:Envelope>
        """
        self._scheme = 'urn:schemas-upnp-org:service:WANIPConnection:1'
        self._header_tmpl = '"{}#'.format(self._scheme) + '{}"'

    def ext_ip(self) -> 'RequestBuilder':
        self._body = """
            <m:GetExternalIPAddress xmlns:m="{}">
            </m:GetExternalIPAddress>
        """.format(self._scheme)
        self._header = 'GetExternalIPAddress'
        return self

    def get_port_mapping(self, port_index: int) -> 'RequestBuilder':
        """
        Args:
            port_index: starting from 0.
        """
        self._body = """
            <m:GetGenericPortMappingEntry xmlns:m="{}">
                <NewPortMappingIndex>{}</NewPortMappingIndex>
            </m:GetGenericPortMappingEntry>
        """.format(self._scheme, port_index)
        self._header = 'GetGenericPortMappingEntry'
        return self

    def add_port_mapping(self, mapping: PortMapping) -> 'RequestBuilder':
        self._body = """
            <m:AddPortMapping xmlns:m="{}">
                <NewRemoteHost></NewRemoteHost>
                <NewExternalPort>{ext_port}</NewExternalPort>
                <NewProtocol>{protocol}</NewProtocol>
                <NewInternalPort>{int_port}</NewInternalPort>
                <NewInternalClient>{ip}</NewInternalClient>
                <NewEnabled>1</NewEnabled>
                <NewPortMappingDescription>{description}</NewPortMappingDescription>
                <NewLeaseDuration>{duration}</NewLeaseDuration>
            </u:AddPortMapping>
        """.format(self._scheme,
                   ext_port=mapping.external_port,
                   protocol=mapping.protocol.upper(),
                   int_port=mapping.internal_port,
                   ip=mapping.ip,
                   description=mapping.description,
                   duration=mapping.duration,
                   )
        self._header = 'AddPortMapping'
        return self

    def delete_port_mapping(self, ext_port: int,
                            protocol: str) -> 'RequestBuilder':
        self._body = """
            <m:DeletePortMapping xmlns:m="{}">
                <NewRemoteHost></NewRemoteHost>
                <NewExternalPort>{ext_port}</NewExternalPort>
                <NewProtocol>{protocol}</NewProtocol>
            </u:DeletePortMapping>
        """.format(self._scheme, ext_port=ext_port, protocol=protocol)
        self._header = 'DeletePortMapping'
        return self

    def body(self) -> str:
        """Constructs request body."""
        return self._body_tmpl.format(self._body)

    def header(self) -> str:
        """Constructs request HTTP header."""
        return self._header_tmpl.format(self._header)


def parse_port_mapping(xml_resp: bytes) -> PortMapping:
    doc = BeautifulSoup(xml_resp, 'lxml-xml')
    return PortMapping(
        remote_host=doc.NewRemoteHost.string,
        external_port=int(doc.NewExternalPort.string),
        internal_port=int(doc.NewInternalPort.string),
        protocol=doc.NewProtocol.string,
        ip=doc.NewInternalClient.string,
        enabled=bool(int(doc.NewEnabled.string)),
        description=doc.NewPortMappingDescription.string,
        duration=int(doc.NewLeaseDuration.string),
    )
