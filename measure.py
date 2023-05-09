#! /usr/bin/env python

from settings import EXPERIMENT, SAMPLES, ITERATIONS
from program import RAM
from prog_lw_hit import RAM as HIT_RAM
from prog_lw_miss import RAM as MISS_RAM
from connection import PulpinoConnection
import chipwhisperer as cw

import numpy as np
from tqdm import trange

DO_CLOCK_CYCLE_CMP = False

scopes = [
    cw.scope(sn = '50203220313038543230373132313036'), # Upper Probe (Core)
    cw.scope(sn = '50203120324136503130313134323031'), # Lower Probe (Cache)
]

bitpath = "./set_associative_cache.bit"
pulpino = PulpinoConnection(bitpath, scope = scopes[0], force = True)

if not pulpino.get_raw().fpga.isFPGAProgrammed():
    print("ERR: FPGA failed to program")
    exit(1)


# Now the PULPINO is running

for scope in scopes:
    scope.gain.db = 30
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

exp_ram = [ MISS_RAM, HIT_RAM ]
assert len(exp_ram) == len(EXPERIMENT)

data = []

if DO_CLOCK_CYCLE_CMP:
    for exp_idx, experiment in enumerate(EXPERIMENT):
        # Reset the PULPINO
        pulpino.reset()

        # Program the RAM address at an offset of 0x0
        pulpino.program(0x0, exp_ram[exp_idx])

        # Stop Programming
        pulpino.stop_programming()

        # Entry Address
        pulpino.send_word(0x0)

        for scope in scopes:
            scope.arm()

        pulpino.send_byte(0x10 | exp_idx)

        for scope in scopes:
            ret = scope.capture()

            if ret:
                print("Failed to capture")
                exit(1)
        
        clock_cycles = pulpino.receive_word()
        
        print(f"Clock Cycles for '{experiment}': {clock_cycles}")

for exp_idx, experiment in enumerate(EXPERIMENT):
    print(f"Running experiment '{experiment}'")

    # Reset the PULPINO
    pulpino.reset()

    # Program the RAM address at an offset of 0x0
    pulpino.program(0x0, exp_ram[exp_idx])

    # Stop Programming
    pulpino.stop_programming()

    # Entry Address
    pulpino.send_word(0x0)

    exp_data = [
        np.empty((ITERATIONS, SAMPLES), dtype=np.float64),
        np.empty((ITERATIONS, SAMPLES), dtype=np.float64),
        # np.zeros(SAMPLES),
        # np.zeros(SAMPLES),
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
            exp_data[i][j] = wave.astype(np.float64, copy=False)
    
    data.append(exp_data)

np.save('mv-xor-nop', data)

for scope in scopes:
    scope.dis()