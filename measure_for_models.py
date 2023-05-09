#! /usr/bin/env python

from os import listdir
from os.path import isfile, join

import numpy as np
from tqdm import trange
from scopes import get_scopes
from connection import PulpinoConnection

MODELS_PATH = './models'

ITERATIONS = 10_000
SAMPLES = 50

scopes = get_scopes()

def measure_traces(pulpino, ram):
    # Reset the PULPINO
    pulpino.reset()

    # Program the RAM address at an offset of 0x0
    pulpino.program(0x0, ram)

    # Stop Programming
    pulpino.stop_programming()

    # Entry Address
    pulpino.send_word(0x0)

    exp_data = [
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

            exp_data[i][j] = wave.astype(np.float64, copy=False)
    
    return exp_data

bitpath = "./set_associative_cache.bit"
pulpino = PulpinoConnection(bitpath, scope = scopes[0], force = True)

if not pulpino.get_raw().fpga.isFPGAProgrammed():
    print("ERR: FPGA failed to program")
    exit(1)

models = [f for f in listdir(MODELS_PATH) if isfile(join(MODELS_PATH, f))]
for model in models:
    untriggered_ram = __import__(f"{model}-untriggered")
    untriggered_ram = untriggered_ram.RAM

    triggered_ram = __import__(f"{model}-triggered")
    triggered_ram = triggered_ram.RAM

    print(f"Running for model '{model}'...")

    untriggered_traces = measure_traces(pulpino, untriggered_ram)
    triggered_traces = measure_traces(pulpino, triggered_ram)

    np.save(f'./models/raw_data/{model}-untriggered', untriggered_traces)
    np.save(f'./models/raw_data/{model}-triggered', triggered_traces)