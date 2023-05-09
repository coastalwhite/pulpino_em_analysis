#! /usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from analysis import extract_model, sliding_window
from settings import SAMPLES, ITERATIONS, SCOPE_NAME, AVG_WINDOW, EXPERIMENT

from os import listdir
from os.path import isfile, join

DO_Y_SHIFT = False
MODELS_PATH = './models'
ALL_MODELS = False
MODELS = ['cache_hit', 'cache_miss']

if ALL_MODELS:
    MODELS = [f for f in listdir(MODELS_PATH) if isfile(join(MODELS_PATH, f))]

models = [
    (model, np.load(f'./models/model_traces/{model}.npy')) for model in MODELS
]

def average_trace(traces):
    averages = []
    for i, _ in enumerate(traces):
        average = np.mean(traces[i], axis=0)
        average = np.convolve(average, np.ones(AVG_WINDOW)/AVG_WINDOW, mode='valid')
        averages.append(average)

    return np.array(averages)

data = np.load('data.npy')

data = average_trace(data)

hit = np.load('hit.npy')
miss = np.load('miss.npy')

hit = average_trace(hit)
miss = average_trace(miss)

plt.figure(20)
for name, model in models:
    sliding_windows = [
        sliding_window(data[i], model[i], do_y_shift = DO_Y_SHIFT) for i in range(len(SCOPE_NAME))
    ]

    plt.figure(20)
    plt.plot(np.square(sliding_windows[0]) + np.square(sliding_windows[1]), label = f"{name}")
    for i in range(len(SCOPE_NAME)):
        plt.figure(i)
        plt.plot(sliding_windows[i], label = f"{name} - {SCOPE_NAME[i]}")

plt.figure(20)
plt.legend()
plt.figure(0)
plt.legend()
plt.figure(1)
plt.legend()

plt.figure(21)
plt.plot(hit[0], label = "Hit")
plt.plot(miss[0], label = "Miss")
plt.plot(np.abs(hit[0] - miss[0]), label = "Difference")

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