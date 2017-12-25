from hamcrest import assert_that, is_

import curio

from igd import Gateway, soap

from utils import AsyncMock


def describe_Gateway():
    def describe_get_port_mappings():
        def it_collects_port_mappings_by_index_until_index_argument_error_is_raised():
            gateway = Gateway('http://dummy/igd', '192.168.1.100')
            gateway.get_port_mapping = AsyncMock(
                async_side_effect=[1, 2, 3, soap.InvalidArgsError(402, '')])

            mappings = curio.run(gateway.get_port_mappings)

            assert_that(mappings, is_([1, 2, 3]))
