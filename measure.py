#! /usr/bin/env python

from settings import EXPERIMENT, SAMPLES, ITERATIONS
from program import RAM
from connection import PulpinoConnection
from scopes import get_scopes, configure_scopes
import chipwhisperer as cw

import numpy as np
from tqdm import trange

DO_CLOCK_CYCLE_CMP = False

scopes = get_scopes()

bitpath = "./set_associative_cache.bit"
pulpino = PulpinoConnection(bitpath, scope = scopes[0], force = True)

if not pulpino.get_raw().fpga.isFPGAProgrammed():
    print("ERR: FPGA failed to program")
    exit(1)

configure_scopes(scopes, SAMPLES)

# Reset the PULPINO
pulpino.reset()

# Program the RAM address at an offset of 0x0
pulpino.program(0x0, RAM)

# Stop Programming
pulpino.stop_programming()

# Entry Address
pulpino.send_word(0x0)

data = [
    np.empty((ITERATIONS, SAMPLES), dtype=np.float64),
    np.empty((ITERATIONS, SAMPLES), dtype=np.float64),
]

for j in trange(ITERATIONS):
    for scope in scopes:
        scope.arm()

    pulpino.send_byte(0)

    for i, scope in enumerate(scopes):
        ret = scope.capture()

        if ret:
            print("Failed to capture")
            exit(1)

        wave = scope.get_last_trace()
        
        if not isinstance(wave, np.ndarray):
            print("[ERROR]: Invalid array type")
            exit(1)

        # exp_data[i] += wave.astype(np.float64, copy=False)
        data[i][j] = wave.astype(np.float64, copy=False)

for scope in scopes:
    scope.dis()

np.save('data', data)