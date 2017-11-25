import curio

from . import ssdp, proto, soap


def main() -> None:
    gateway = curio.run(ssdp.find_gateway)
    ext_ip = curio.run(gateway.get_ext_ip)
    print(ext_ip)
    port_mapping = curio.run(gateway.get_port_mapping, 0)
    print(port_mapping)


main()
