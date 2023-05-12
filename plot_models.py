#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from scopes import CACHE_PROBE, NUM_PROBES
from settings import SCOPE_NAME
from model import all_models
from analysis import extract_model, avg_traces, identify_cache_miss_pattern

models = all_models()
for i, model in enumerate(models):
    waveform = model.load_waveform()
    offset = waveform.probe_offset
    duration = waveform.len()

    plt.figure(i)
    plt.title(f"Model Waveform for '{model.name}'")

    if offset == 0:
        plt.plot(waveform.waveforms[0], label = SCOPE_NAME[0])
        plt.plot(waveform.waveforms[1], label = SCOPE_NAME[1])

        if model.name == 'multiple_loads':
            dy, chance = identify_cache_miss_pattern(waveform.waveforms[CACHE_PROBE])
            plt.plot(dy, label = "DY")
            plt.plot(chance, label = "Cache Miss Chance")
    elif offset > 1:
        plt.plot(range(0, duration), waveform.waveforms[0], label = SCOPE_NAME[0])
        plt.plot(range(offset, offset + duration), waveform.waveforms[1], label = SCOPE_NAME[1])
    else:
        plt.plot(range(abs(offset), abs(offset) + duration), waveform.waveforms[0], label = SCOPE_NAME[0])
        plt.plot(range(0, duration), waveform.waveforms[1], label = SCOPE_NAME[1])

    plt.legend()

plt.show()