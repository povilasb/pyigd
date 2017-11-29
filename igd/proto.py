from xml.dom.minidom import parseString
from bs4 import BeautifulSoup


def get_ext_ip() -> str:
    header = '"urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress"'
    body = """<?xml version="1.0"?>
    <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
        <s:Body>
            <m:GetExternalIPAddress xmlns:m="urn:schemas-upnp-org:service:WANIPConnection:1">
            </m:GetExternalIPAddress>
        </s:Body>
    </s:Envelope>
    """
    return header, body


def parse_ext_ip(xml_resp: bytes) -> str:
    doc = BeautifulSoup(xml_resp, 'lxml-xml')
    return doc.NewExternalIPAddress.string


def get_port_mapping(i: int) -> str:
    header = '"urn:schemas-upnp-org:service:WANIPConnection:1#GetGenericPortMappingEntry"'
    body = """<?xml version="1.0"?>
    <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
        <s:Body>
            <m:GetGenericPortMappingEntry xmlns:m="urn:schemas-upnp-org:service:WANIPConnection:1">
                <NewPortMappingIndex>{}</NewPortMappingIndex>
            </m:GetGenericPortMappingEntry>
        </s:Body>
    </s:Envelope>
    """.format(i)
    return header, body


class PortMapping:
    def __init__(self, remote_host: str, external_port: int,
                 internal_port: int, protocol: str, ip: str, enabled: bool,
                 description: str, duration: int):
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
