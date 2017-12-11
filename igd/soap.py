import asks
from bs4 import BeautifulSoup


class Error(Exception):
    """SOAP error."""

    def __init__(self, code: int, msg: str) -> None:
        super().__init__(msg)
        self.code = code


class Response:
    """SOAP response."""

    def __init__(self, body: str, status_code: int) -> None:
        self.body = body
        self.status_code = status_code

    def xml(self) -> BeautifulSoup:
        """
        Returns:
            xml document build from response body.
        """
        return BeautifulSoup(self.body, 'lxml-xml')


async def post(url: str, msg: str, soap_action: str) -> Response:
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
    return Response(resp.content, resp.status_code)


def _validate_response(resp: asks.response_objects.Response) -> None:
    if resp.status_code == 500:
        doc = BeautifulSoup(resp.content, 'lxml-xml')
        err_code = int(doc.errorCode.string)
        err_msg = doc.errorDescription.string
        raise Error(err_code, err_msg)
