#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from model import all_models

from analysis import avg_traces, identify_cache_miss_pattern, sliding_window, sliding_windows_to_measure
from settings import SCOPE_NAME, CLOCK_CYCLE_LENGTH
from scopes import CACHE_PROBE

NUM_SCOPES = len(SCOPE_NAME)

# Leave empty to load all models
MODELS = [
    'cache_hit',
    'cache_miss',
    'xor',
]

models = all_models()
if len(MODELS) != 0:
    # Only allow models from `MODELS`
    models = list(filter(lambda model : model.name in MODELS, models))

    # Make sure that all models in `MODELS` are present
    for needed_model in MODELS:
        if not any(map(lambda model: model.name == needed_model, models)):
            print(f"[ERROR]: Model '{needed_model}' not found!")
            exit(1)

def average_trace(traces):
    averages = []
    for i, _ in enumerate(traces):
        average = avg_traces(traces[i])
        averages.append(average)

    return np.array(averages)

def stddev_trace(traces):
    stddev = []
    for i, _ in enumerate(traces):
        std = np.std(traces[i], axis=0)
        stddev.append(std)
    return np.array(stddev)

data = np.load('data.npy')

stddev = stddev_trace(data)
data = average_trace(data)

hit = np.load('hit.npy')
miss = np.load('miss.npy')

hit = average_trace(hit)
miss = average_trace(miss)

# sws = []

# plt.figure(20)
for model in models:
    model_waveform = model.load_waveform()
    
    sliding_windows = [
        sliding_window(
            data[i],
            model_waveform.waveforms[i],
        ) for i in range(len(SCOPE_NAME))
    ]

    interwave_offset = model_waveform.probe_offset

    measure = sliding_windows_to_measure(
        sliding_windows[0],
        sliding_windows[1],
        interwave_offset,
    )

    plt.figure(20)
    plt.plot(measure, label = f"{model.name}")
    # for i in range(len(SCOPE_NAME)):
    #     plt.figure(i)
    #     plt.plot(sliding_windows[i], label = f"{model.name} - {SCOPE_NAME[i]}")
    # sws.append(sliding_windows)

# plt.figure(21)
# plt.plot(np.abs(sws[0][0] - sws[1][0]))
# plt.plot(np.abs(sws[0][1] - sws[1][1]))
# plt.title("DIFF")

plt.figure(20)
plt.xlim(0, CLOCK_CYCLE_LENGTH)
plt.legend()
# plt.figure(0)
# plt.xlim(0, CLOCK_CYCLE_LENGTH)
# plt.legend()
# plt.figure(1)
# plt.xlim(0, CLOCK_CYCLE_LENGTH)
# plt.legend()

plt.figure(50)
cache_trace = data[CACHE_PROBE]
dy, cache_miss_trace = identify_cache_miss_pattern(cache_trace)
plt.plot(cache_miss_trace, label = "Chance at cache miss")
plt.title("Cache Miss Trace")
plt.xlim(0, CLOCK_CYCLE_LENGTH)
plt.legend()

plt.figure(30)

hit = hit[0] * hit[1]
miss = miss[0] * miss[1]

# plt.plot(hit, label = f"Hit")
# plt.plot(miss, label = f"Miss")
plt.plot(np.abs(hit - miss), label = f"Difference")
plt.xlim(0, CLOCK_CYCLE_LENGTH)
plt.title("Differential Plot Between Opposite Cache access patterns")

plt.legend()

# for i, scope_name in enumerate(SCOPE_NAME):
#     plt.figure(i)
#     plt.plot(abs((data[1][i] - data[0][i])) / ITERATIONS, label = f"{EXPERIMENT[1]} - {EXPERIMENT[0]}")
#     for exp_idx, experiment in enumerate(EXPERIMENT):
#         plt.plot(data[exp_idx][i] / ITERATIONS, label = experiment)
#     plt.title(f"{scope_name} Probe")
#     plt.xlabel("Samples / Clock Cycles")
#     plt.ylabel("Volts")
#     plt.xlim(AVG_WINDOW, SAMPLES - AVG_WINDOW)
#     plt.legend()

plt.show()