from unittest.mock import MagicMock, patch

from hamcrest import assert_that, is_, calling, raises
import curio

from igd import soap

from utils import AsyncMock


def describe_Error():
    def describe__str__():
        def it_formats_message_and_error_code():
            err = soap.Error(402, 'Invalid args')

            assert_that(str(err), is_('"Invalid args", error code: 402'))


def describe_Response():
    def describe_xml():
        def it_returns_response_body_parsed_to_beautifulsoap_xml_object():
            resp = soap.Response(b'<xml><data>content</data></xml>', 200)

            doc = resp.xml()

            assert_that(doc.data.string, is_('content'))


def describe_post():
    def it_returns_successfull_responses():
        resp = MagicMock(content=b'xml', status_code=200)

        with patch('asks.post', AsyncMock(async_return_value=resp)):
            soap_resp = curio.run(
                soap.post, 'http://192.168.0.1:1900/ipc', '<xml></xml>',
                '"urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIpAddress"'
            )

            assert_that(soap_resp.status_code, is_(200))
            assert_that(soap_resp.body, is_(b'xml'))


def describe__validate_response():
    def describe_when_response_code_is_500():
        def describe_and_soap_error_is_402():
            def it_raises_invalid_args_error():
                resp = MagicMock()
                resp.status_code = 500
                resp.content = b"""
                    <xml>
                        <errorCode>402</errorCode>
                        <errorDescription>Invalid args</errorDescription>
                    </xml>
                """

                assert_that(
                    calling(soap._validate_response).with_args(resp),
                    raises(soap.InvalidArgsError)
                )

        def describe_and_soap_error_is_some_unknown_error():
            def it_raises_generic_soap_error():
                resp = MagicMock()
                resp.status_code = 500
                resp.content = b"""
                    <xml>
                        <errorCode>999</errorCode>
                        <errorDescription>Invalid args</errorDescription>
                    </xml>
                """

                assert_that(
                    calling(soap._validate_response).with_args(resp),
                    raises(soap.Error)
                )

    def describe_when_response_code_is_not_200():
        def it_raises_http_error():
            resp = MagicMock()
            resp.status_code = 401
            resp.content = b''

            assert_that(
                calling(soap._validate_response).with_args(resp),
                raises(soap.HttpError)
            )

    def describe_when_response_code_is_200():
        def it_returns_silently():
            resp = MagicMock()
            resp.status_code = 200
            resp.content = b'OK'

            soap._validate_response(resp)
