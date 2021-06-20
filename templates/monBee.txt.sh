#!/bin/sh
node monBee/monBee.js {% for account in accounts %}{% set api_addr = (loop.index0 * 3) + network.base_host_port %}{% set p2p_addr = api_addr + 1 %}{% set debug_api_addr = p2p_addr + 1 %}{% set nat_addr = loop.index0 + network.base_external_port %} http://localhost:{{ debug_api_addr }}{% endfor %} $@ 2>>monBee.err
