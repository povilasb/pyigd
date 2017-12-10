from unittest.mock import patch, MagicMock

from hamcrest import assert_that, is_
import curio

from igd.proto import PortMapping
from igd.core import _port_mapping_to_arr, delete_port_mapping

from utils import AsyncMock


def describe__port_mapping_to_arr():
    def it_returns_port_mapping_fields_as_array_ready_to_be_printed():
        mapping = PortMapping(None, 5000, 6000, 'TCP', '192.168.1.10', True,
                              'test mapping', 0)

        values = _port_mapping_to_arr(mapping)

        assert_that(
            values,
            is_(['test mapping', 5000, 'TCP', 6000, '192.168.1.10', 'Enabled'])
        )


def describe_delete_port_mapping():
    def describe_when_protocol_is_not_specified():
        def it_deletes_mappings_for_all_possible_protocols():
            gateway = AsyncMock()

            with patch('igd.ssdp.find_gateway', AsyncMock(async_return_value=gateway)):
                curio.run(delete_port_mapping(4000, None))

                gateway.delete_port_mapping.assert_any_call(4000, 'TCP')
                gateway.delete_port_mapping.assert_any_call(4000, 'UDP')

    def describe_when_protocol_is_specified():
        def it_deletes_mapping_for_given_port_and_protocol():
            gateway = AsyncMock()

            with patch('igd.ssdp.find_gateway', AsyncMock(async_return_value=gateway)):
                curio.run(delete_port_mapping(4000, 'TCP'))

                gateway.delete_port_mapping.assert_called_with(4000, 'TCP')
