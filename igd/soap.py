from xml.dom.minidom import parseString

import asks

from . import proto


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
        err_dom = parseString(resp.content)
        err_code = proto._node_value(err_dom.getElementsByTagName('errorCode')[0])
        err_msg = proto._node_value(
            err_dom.getElementsByTagName('errorDescription')[0]
        )
        raise Exception(
            'SOAP request error: {0} - {1}'.format(err_code, err_msg)
        )
