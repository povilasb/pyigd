=====
About
=====

.. image:: https://travis-ci.org/povilasb/pyigd.svg?branch=master
    :target: https://travis-ci.org/povilasb/pyigd
.. image:: https://coveralls.io/repos/github/povilasb/pyigd/badge.svg?branch=master
    :target: https://coveralls.io/github/povilasb/pyigd?branch=master

This is a small python based tool to interact with IGD capable devices.
IGD is protocol, usually supported by routers, that allows you to:

* Learn the public (external) IP address
* Enumerate existing port mappings
* Add and remove port mappings

This tool aims to be simple, clean, easy to install, hackable tool. Hence, CI is
enabled, test coverage should be kept to the maximum, code is linted, types are
checked, open source liraries are reused, etc.

Sorry, no Python 2 support.

Install
=======

::

    $ pip3 install igd

or if you want to get latest development changes::

    $ pip3 install git+https://github.com/povilasb/pyigd

Usage
=====

.. image:: usage.gif

`igd` aims for ergonomic usage with convenient defaults but also tries to
give full control over how ports are mapped, listed and removed.

For more detailed description just use the `--help` option for each command::

    $igd --help
    Usage: igd [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      add  Add new port mapping.
      ip   Get external IP from IGD.
      ls   Get all port mappings.
      rm   Remove port mapping.

Other projects
==============

Other quite usable projects that I found to work:

* https://github.com/SBSTP/rust-igd
* https://github.com/miniupnp/miniupnp

References
==========

* https://en.wikipedia.org/wiki/Internet_Gateway_Device_Protocol
* https://tools.ietf.org/html/draft-cai-ssdp-v1-03
* https://tools.ietf.org/html/rfc6970
* http://www.upnp.org/specs/gw/UPnP-gw-WANIPConnection-v1-Service.pdf
* http://www.upnp-hacks.org
