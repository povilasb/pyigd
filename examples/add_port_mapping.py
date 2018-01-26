# An example that adds port mapping using IGD protocol.
#
# After running this script port mapping table should look like:
#
# $ igd ls
# Description      External Port  Protocol      Internal Port  IP             Status
# -------------  ---------------  ----------  ---------------  -------------  --------
# test                      5000  TCP                    5000  192.168.1.210  Enabled
#
# Requirements:

#   pip install igd

import igd
import curio


async def main():
    gateway = await igd.find_gateway()
    print('Located:', gateway)

    internal_port = 5000
    external_port = 5000
    ip = '192.168.1.210'
    duration_in_seconds = 20
    description = 'test'
    enabled = True
    mapping = igd.proto.PortMapping('', internal_port, external_port, 'TCP', ip,
                                enabled, description, duration_in_seconds)
    await gateway.add_port_mapping(mapping)
    print('Success!')


curio.run(main)
