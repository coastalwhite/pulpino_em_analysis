#! /usr/bin/env python

import numpy as np

from scopes import CORE_PROBE, CACHE_PROBE, NUM_PROBES
from settings import SAMPLES_PER_CC
from model import all_models, ModelWaveForm
from analysis import extract_model, avg_traces

models = all_models()
for model in models:
    # Load the data from the measurements
    untriggered_traces = model.load_untriggered_trace()
    triggered_traces = model.load_triggered_trace()

    # Average over all the measurements
    untriggered_traces = [
        avg_traces(untriggered_traces[i]) for i in range(NUM_PROBES)
    ]
    triggered_traces = [
        avg_traces(triggered_traces[i]) for i in range(NUM_PROBES)
    ]

    window_size = model.duration_target

    extracted_models = [
        extract_model(
            triggered_traces[i],
            untriggered_traces[i],
            window_size,
            model.duration_prologue,
        ) for i in range(NUM_PROBES)
    ]

    # # Offset between the start of interval of cache and core probes
    # interwave_offset = int(
    #     extracted_models[CORE_PROBE].index -
    #     extracted_models[CACHE_PROBE].index
    # )
    #
    # # If the distance is too high, there might be a problem with the probing
    # if abs(interwave_offset) > window_size:
    #     print(f"[WARNING]: Mismatch between probes trigger offsets for '{model.name}' model")

    waveforms = np.array([
        extracted_models[i].wave for i in range(NUM_PROBES)
    ])

    waveform = ModelWaveForm(waveforms, 0)#interwave_offset)
    model.save_waveform(waveform)
