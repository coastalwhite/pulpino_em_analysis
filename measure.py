#! /usr/bin/env python

from settings import SAMPLES, TARGET_ITERATIONS as ITERATIONS, BIT_FILE
from program import RAM
from connection import PulpinoConnection
from scopes import get_scopes, capture_traces

import numpy as np

scopes = get_scopes()

pulpino = PulpinoConnection(BIT_FILE, scope = scopes[0], force = True)

if not pulpino.get_raw().fpga.isFPGAProgrammed():
    print("ERR: FPGA failed to program")
    exit(1)

probe_waveforms = capture_traces(
    scopes,
    pulpino,
    RAM,
    ITERATIONS,
    SAMPLES,
)

for scope in scopes:
    scope.dis()

np.save('data', probe_waveforms)