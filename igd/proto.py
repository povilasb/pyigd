from typing import Tuple

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


def add_port_mapping(mapping: PortMapping) -> Tuple[str, str]:
    """
    Note: skips remote host field, because I wasn't sure about def it's use.
    """
    header = '"urn:schemas-upnp-org:service:WANIPConnection:1#AddPortMapping"'
    body = """<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
        <u:AddPortMapping xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
            <NewRemoteHost></NewRemoteHost>
            <NewExternalPort>{ext_port}</NewExternalPort>
            <NewProtocol>{protocol}</NewProtocol>
            <NewInternalPort>{int_port}</NewInternalPort>
            <NewInternalClient>{ip}</NewInternalClient>
            <NewEnabled>1</NewEnabled>
            <NewPortMappingDescription>{description}</NewPortMappingDescription>
            <NewLeaseDuration>{duration}</NewLeaseDuration>
        </u:AddPortMapping>
    </s:Body>
</s:Envelope>""".format(
        ext_port=mapping.external_port,
        protocol=mapping.protocol,
        int_port=mapping.internal_port,
        ip=mapping.ip,
        description=mapping.description,
        duration=mapping.duration,
    )
    return header, body


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
