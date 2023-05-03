#!/bin/sh

git submodule update --init
ln -sf $PWD/pulpino-top-level-cw305/program/ext/connection.py connection.py
ln -sf $PWD/pulpino-top-level-cw305/program/target/out/power_trace program.py