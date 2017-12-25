from unittest.mock import patch, MagicMock, ANY
import io

from hamcrest import assert_that, is_
import pytest
import curio

from igd.proto import PortMapping
from igd.core import _port_mapping_to_arr, delete_port_mappings
from igd import core, soap

from utils import AsyncMock


def describe_handle_exceptions():
    def describe_when_given_function_succeeds():
        def it_returns_what_function_returns():
            @core.handle_exceptions
            async def func():
                return 10

            retval = curio.run(func)

            assert_that(retval, is_(10))

    def describe_when_expected_exceptions_happen():
        @patch('sys.stdout', MagicMock())
        @pytest.mark.parametrize('error', [
            soap.HttpError(500, 'Server error'),
            soap.InvalidArgsError(402, 'Invalid args')
        ])
        def it_makes_wrapped_function_not_to_fail(error):
            @core.handle_exceptions
            async def func():
                raise error

            curio.run(func)

def describe_get_ip():
    def it_prints_external_ip_address():
        gateway = AsyncMock()
        gateway.get_ext_ip.async_return_value = '1.2.3.4'

        with patch('igd.ssdp.find_gateway', AsyncMock(async_return_value=gateway)):
            with patch('sys.stdout', new_callable=io.StringIO) as out:
                curio.run(core.get_ip)

                assert_that(out.getvalue(), is_('1.2.3.4\n'))


def describe__port_mapping_to_arr():
    def it_returns_port_mapping_fields_as_array_ready_to_be_printed():
        mapping = PortMapping(None, 5000, 6000, 'TCP', '192.168.1.10', True,
                              'test mapping', 0)

        values = _port_mapping_to_arr(mapping)

        assert_that(
            values,
            is_(['test mapping', '5000', 'TCP', '6000', '192.168.1.10', 'Enabled'])
        )


def describe_delete_port_mappings():
    def describe_when_pattern_is_port():
        def describe_when_protocol_is_not_specified():
            @patch('igd.ssdp.find_gateway', AsyncMock())
            def it_deletes_mappings_for_all_possible_protocols():
                with patch('igd.core._delete_port_mappings_by_port',
                           AsyncMock()) as delete_mappings:
                    curio.run(delete_port_mappings('4000', None))

                    delete_mappings.assert_called_with(ANY, 4000, ['TCP', 'UDP'])

        def describe_when_protocol_is_specified():
            @patch('igd.ssdp.find_gateway', AsyncMock())
            def it_deletes_mapping_for_given_port_and_protocol():
                with patch('igd.core._delete_port_mappings_by_port',
                           AsyncMock()) as delete_mappings:
                    curio.run(delete_port_mappings('4000', 'TCP'))

                    delete_mappings.assert_called_with(ANY, 4000, ['TCP'])

    def describe_when_pattern_is_any_other_string():
        @patch('igd.ssdp.find_gateway', AsyncMock())
        def it_deletes_mappings_by_description():
            with patch('igd.core._delete_port_mappings_by_description',
                       AsyncMock()) as delete_mappings:
                curio.run(delete_port_mappings('Skype', None))

                delete_mappings.assert_called_with(ANY, 'Skype', ['TCP', 'UDP'])


def describe__delete_port_mappings_by_port():
    def it_deletes_port_for_every_given_protocol():
        gateway = AsyncMock()

        curio.run(core._delete_port_mappings_by_port(gateway, 4000, ['TCP', 'UDP']))

        gateway.delete_port_mapping.assert_any_call(4000, 'TCP')
        gateway.delete_port_mapping.assert_any_call(4000, 'UDP')

    def describe_soap_error_is_received():
        def describe_when_error_is_invalid_args():
            def it_continues_silently():
                gateway = AsyncMock()
                gateway.delete_port_mapping.side_effect = soap.InvalidArgsError(
                    soap.ERROR_INVALID_ARGS, 'test error')

                curio.run(core._delete_port_mappings_by_port(gateway, 4000, ['TCP']))

        def describe_when_error_is_unknown():
            def it_reraises_it():
                gateway = AsyncMock()
                gateway.delete_port_mapping.side_effect = soap.Error(999, 'test error')

                async def del_port():
                    try:
                        await core._delete_port_mappings_by_port(gateway, 4000, ['TCP'])
                    except soap.Error as e:
                        assert_that(e.code, is_(999))

                curio.run(del_port)


def describe__delete_port_mappings_by_description():
    def it_deletes_all_mappings_whose_description_match_given_pattern():
        gateway = AsyncMock()
        gateway.get_port_mappings = AsyncMock(async_return_value=[
            PortMapping(None, 1, 1, 'TCP', '192.168.1.10', True, 'mapping', 0),
            PortMapping(None, 2, 2, 'TCP', '192.168.1.10', True, 'Skype', 0),
            PortMapping(None, 3, 3, 'UDP', '192.168.1.10', True, 'mapping', 0),
        ])

        curio.run(core._delete_port_mappings_by_description(
            gateway, 'mapping', ['TCP', 'UDP']))

        gateway.delete_port_mapping.assert_any_call(1, 'TCP')
        gateway.delete_port_mapping.assert_any_call(3, 'UDP')

    def describe_when_not_all_ports_are_specified():
        def it_deletes_only_mappings_whose_description_and_protocol_match():
            gateway = AsyncMock()
            gateway.get_port_mappings = AsyncMock(async_return_value=[
                PortMapping(None, 1, 1, 'TCP', '192.168.1.10', True, 'mapping', 0),
                PortMapping(None, 2, 2, 'TCP', '192.168.1.10', True, 'Skype', 0),
                PortMapping(None, 3, 3, 'UDP', '192.168.1.10', True, 'mapping', 0),
            ])

            curio.run(core._delete_port_mappings_by_description(
                gateway, 'mapping', ['TCP']))

            gateway.delete_port_mapping.assert_called_with(1, 'TCP')
