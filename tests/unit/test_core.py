from hamcrest import assert_that, is_

from igd.proto import PortMapping
from igd.core import _port_mapping_to_arr


def describe__port_mapping_to_arr():
    def it_returns_port_mapping_fields_as_array_ready_to_be_printed():
        mapping = PortMapping(None, 5000, 6000, 'TCP', '192.168.1.10', True,
                              'test mapping', 0)

        values = _port_mapping_to_arr(mapping)

        assert_that(
            values,
            is_(['test mapping', 5000, 'TCP', 6000, '192.168.1.10', 'Enabled'])
        )
