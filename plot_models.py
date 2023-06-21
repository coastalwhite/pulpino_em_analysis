#! /usr/bin/env python

import matplotlib.pyplot as plt

import sys

from scopes import NUM_PROBES 
from settings import SCOPE_NAME
from model import all_models

models = all_models()
if len(sys.argv) > 1:
    selected = sys.argv[1:]
    for i in range(len(selected)):
        if selected[i].endswith('.rvmdl'):
            selected[i] = selected[i][:-len('.rvmdl')]
    
    models = list(filter(lambda model : model.name in selected, models))

for i, model in enumerate(models):
    waveform = model.load_waveform()
    offset = waveform.probe_offset
    duration = waveform.len()

    plt.figure(i)
    plt.title(f"Model Waveform for '{model.name}'")

    if offset == 0:
        for i in range(NUM_PROBES):
            plt.plot(waveform.waveforms[i], label = SCOPE_NAME[i])
    else:
        print("[ERROR]: Interwave offset")
        exit(1)

    plt.legend()

plt.show()