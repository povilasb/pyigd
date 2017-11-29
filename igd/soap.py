import asks
from bs4 import BeautifulSoup

from . import proto


class Error(Exception):
    """SOAP error."""

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(msg)
        self.code = code


async def post(url: str, msg: str, soap_action: str) -> bytes:
    """
    Args:
        msg: SOAP xml based message.
        soap_action: SOAPAction header.

    Returns:
        XML formatted response.
    """
    headers = {
        'SOAPAction': soap_action,
        'Content-Type': 'text/xml'
    }
    resp = await asks.post(url, data=msg, headers=headers)
    _validate_response(resp)
    return resp.content


def _validate_response(resp: asks.response_objects.Response) -> None:
    if resp.status_code == 500:
        doc = BeautifulSoup(resp.content, 'lxml-xml')
        err_code = int(doc.errorCode.string)
        err_msg = doc.errorDescription.string
        raise Error(err_code, err_msg)
