#! /usr/bin/env python

from program import RAM
from connection import PulpinoConnection
import chipwhisperer as cw

import numpy as np
from tqdm import trange
import matplotlib.pyplot as plt

ITERATIONS = 1_000
SAMPLES = 20_000

scopes = [
    cw.scope(sn = '50203220313038543230373132313036'),
    cw.scope(sn = '50203120324136503130313134323031'),
]

bitpath = "./set_associative_cache.bit"
pulpino = PulpinoConnection(bitpath, scope = scopes[0], force = True)

if not pulpino.get_raw().fpga.isFPGAProgrammed():
    print("ERR: FPGA failed to program")
    exit(1)

# Reset the PULPINO
pulpino.reset()

# Program the RAM address at an offset of 0x0
pulpino.program(0x0, RAM)

# Stop Programming
pulpino.stop_programming()

# Entry Address
pulpino.send_word(0x0)

# Now the PULPINO is running

for scope in scopes:
    scope.gain.db = 20
    scope.gain.gain = 60
    scope.gain.mode = "high"

    scope.adc.samples = SAMPLES
    scope.adc.offset = 0
    scope.adc.basic_mode = "rising_edge"
    scope.adc.timeout = 2

    scope.clock.clkgen_src = "extclk"
    scope.clock.freq_ctr_src = "extclk"
    # scope.clock.adc_src = "extclk_x4"
    scope.clock.adc_src = "extclk_dir"
    scope.clock.extclk_freq = 20E6

    # scope.io.tio1 = "high_z"
    # scope.io.tio2 = "high_z"
    scope.trigger.triggers = "tio4"
    scope.io.hs2 = "disabled"

    # ensure ADC is locked:
    scope.clock.reset_adc()
    assert (scope.clock.adc_locked), "ADC failed to lock"

# print(scope)

ws = [
    np.zeros(SAMPLES),
    np.zeros(SAMPLES),
]

for _ in trange(ITERATIONS):
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

        ws[i] += wave.astype(np.float64, copy=False)

for scope in scopes:
    scope.dis()

plt.plot(ws[0])
plt.show()

plt.plot(ws[1])
plt.show()