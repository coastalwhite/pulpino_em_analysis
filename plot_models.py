#! /usr/bin/env python

import matplotlib.pyplot as plt

import sys

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
        plt.plot(waveform.waveforms[0], label = SCOPE_NAME[0])
        plt.plot(waveform.waveforms[1], label = SCOPE_NAME[1])
    elif offset > 1:
        plt.plot(range(0, duration), waveform.waveforms[0], label = SCOPE_NAME[0])
        plt.plot(range(offset, offset + duration), waveform.waveforms[1], label = SCOPE_NAME[1])
    else:
        plt.plot(range(abs(offset), abs(offset) + duration), waveform.waveforms[0], label = SCOPE_NAME[0])
        plt.plot(range(0, duration), waveform.waveforms[1], label = SCOPE_NAME[1])

    plt.legend()

plt.show()