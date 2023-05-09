#! /usr/bin/env python

from os import listdir
from os.path import isfile, join

import numpy as np

from analysis import extract_model
from settings import AVG_WINDOW

MODELS_PATH = './models'
PIPELINE_WIDTH = 4

def average_traces(traces):
    mean = np.mean(traces, axis=0)
    windowed = np.convolve(mean, np.ones(AVG_WINDOW)/AVG_WINDOW, mode='valid')

    return windowed

models = [f for f in listdir(MODELS_PATH) if isfile(join(MODELS_PATH, f))]
for model in models:
    untriggered_traces = np.load(f'./models/raw_data/{model}-untriggered.npy')
    triggered_traces = np.load(f'./models/raw_data/{model}-triggered.npy')
    
    untriggered_traces = [
        average_traces(untriggered_traces[0]),
        average_traces(untriggered_traces[1]),
    ]
    triggered_traces = [
        average_traces(triggered_traces[0]),
        average_traces(triggered_traces[1]),
    ]

    extracted_models = [
        extract_model(untriggered_traces[0], triggered_traces[0]),
        extract_model(untriggered_traces[1], triggered_traces[1]),
    ]

    # If the distance is too high, there might be a problem with the probing
    if abs(extracted_models[0].index - extracted_models[1].index) > PIPELINE_WIDTH:
        print("[WARNING]: Mismatch between probes trigger offsets for '{model}' model")
        
    avg_waves = [
        (untriggered_traces[0] + triggered_traces[0]) / 2,
        (untriggered_traces[1] + triggered_traces[1]) / 2,
    ]

    # Pick the probe with the clearest difference as the model
    if extracted_models[0].distance > extracted_models[1].distance:
        traces = [
            extracted_models[0].wave,
            extracted_models[0].matching_wave(avg_waves[1]),
        ]
    else:
        traces = [
            extracted_models[1].wave,
            extracted_models[1].matching_wave(avg_waves[0]),
        ]

    np.save(f'./models/model_traces/{model}', traces)