#! /usr/bin/env python

from program import RAM
from prog_lw_hit import RAM as HIT_RAM
from prog_lw_miss import RAM as MISS_RAM
from connection import PulpinoConnection
import chipwhisperer as cw

import scipy as sp
import numpy as np
from tqdm import trange
import matplotlib.pyplot as plt

DO_CLOCK_CYCLE_CMP = False
ITERATIONS = 1_000
AVG_WINDOW = 4
SAMPLES = 600

scopes = [
    cw.scope(sn = '50203220313038543230373132313036'), # Upper Probe (Core)
    cw.scope(sn = '50203120324136503130313134323031'), # Lower Probe (Cache)
]

scope_names = [
    "Core",
    "Cache",
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

# print(scope)

experiments = [
    "Cache Miss",
    "Cache Hit",
]
exp_ram = [ MISS_RAM, HIT_RAM ]

data = []

if DO_CLOCK_CYCLE_CMP:
    for exp_idx, experiment in enumerate(experiments):
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

for exp_idx, experiment in enumerate(experiments):
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

averages = []
print("Computing running averages...")
for i, _ in enumerate(data):
    exp_averages = []
    for j, _ in enumerate(data[i]):
        average = np.mean(data[i][j], axis=0)
        average = np.convolve(average, np.ones(AVG_WINDOW)/AVG_WINDOW, mode='valid')
        exp_averages.append(average)
    averages.append(exp_averages)
print("Done computing running averages!")

pcc = []
for i in range(2):
    p = []
    for s in range(SAMPLES):
        core_samples_at_time = data[i][0][:, s]
        cache_samples_at_time = data[i][1][:, s]

        cr = sp.stats.pearsonr(core_samples_at_time, cache_samples_at_time).statistic
        p.append(cr)
    pcc.append(p)

data = averages

for scope in scopes:
    scope.dis()

for i, scope_name in enumerate(scope_names):
    plt.figure(i)
    plt.plot(abs((data[1][i] - data[0][i])) / ITERATIONS, label = f"{experiments[1]} - {experiments[0]}")
    for exp_idx, experiment in enumerate(experiments):
        plt.plot(data[exp_idx][i] / ITERATIONS, label = experiment)
    plt.title(f"{scope_name} Probe")
    plt.xlabel("Samples / Clock Cycles")
    plt.ylabel("Volts")
    plt.xlim(AVG_WINDOW, SAMPLES - AVG_WINDOW)
    plt.legend()

for i, d in enumerate(pcc):
    plt.figure(i+2)
    plt.plot(d)
    plt.title(f"Correlation Core and Cache '{experiments[i]}'")
    plt.xlabel("Samples / Clock Cycles")
    plt.ylabel("Pearson Correlation Coefficient")
    # plt.ylim(-1.1, 1.1)

plt.show()