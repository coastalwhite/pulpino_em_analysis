#!/bin/sh

git submodule update --init
ln -sf $PWD/pulpino-top-level-cw305/program/ext/connection.py connection.py
ln -sf $PWD/pulpino-top-level-cw305/program/target/out/power_trace program.py

# Lower the PULPINO frequency from 100MHz to 20MHz
patch $PWD/pulpino-top-level-cw305/program/ext/connection.py < ./lower_freq.patch