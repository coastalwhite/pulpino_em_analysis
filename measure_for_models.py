#! /usr/bin/env python

import numpy as np

from settings import BIT_FILE, SAMPLES_PER_CC, MODEL_ITERATIONS
from scopes import capture_traces, get_scopes
from connection import PulpinoConnection
from model import all_models

BASE_SAMPLES = 200*SAMPLES_PER_CC

scopes = get_scopes()

pulpino = PulpinoConnection(BIT_FILE, scope = scopes[0], force = True)

if not pulpino.get_raw().fpga.isFPGAProgrammed():
    print("ERR: FPGA failed to program")
    exit(1)

models = all_models()
for model in models:
    untriggered_ram = __import__(f"{model.name}-untriggered")
    untriggered_ram = untriggered_ram.RAM

    triggered_ram = __import__(f"{model.name}-triggered")
    triggered_ram = triggered_ram.RAM

    print(f"Running for model '{model.name}'...")

    samples = BASE_SAMPLES + (model.duration_target + model.duration_prologue)*SAMPLES_PER_CC

    untriggered_traces = capture_traces(
        scopes,
        pulpino,
        untriggered_ram,
        MODEL_ITERATIONS,
        samples,
    )
    triggered_traces = capture_traces(
        scopes,
        pulpino,
        triggered_ram,
        MODEL_ITERATIONS,
        samples,
    )

    np.save(f'./models/raw_data/{model.name}-untriggered', untriggered_traces)
    np.save(f'./models/raw_data/{model.name}-triggered', triggered_traces)