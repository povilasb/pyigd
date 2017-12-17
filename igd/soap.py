import asks
from bs4 import BeautifulSoup


# Might happen when:
# * deleting port mapping which does not exist.
ERROR_INVALID_ARGS = 402
ERROR_INVALID_ACTION = 401
ERROR_ACTION_FAILED = 501


class Error(Exception):
    """SOAP error."""

    def __init__(self, code: int, msg: str) -> None:
        self.code = code
        self.message = msg

    def __str__(self) -> str:
        return '"{}", error code: {}'.format(self.message, self.code)


class InvalidArgsError(Error):
    pass


class HttpError(Error):
    pass


class Response:
    """SOAP response."""

    def __init__(self, body: bytes, status_code: int) -> None:
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

        if err_code == ERROR_INVALID_ARGS:
            raise InvalidArgsError(err_code, err_msg)
        raise Error(err_code, err_msg)

    if resp.status_code != 200:
        raise HttpError(resp.status_code, 'Unknwon error')
