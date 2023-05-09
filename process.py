#! /usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from analysis import extract_model, sliding_window
from settings import SAMPLES, ITERATIONS, SCOPE_NAME, AVG_WINDOW, EXPERIMENT

data = np.load('mv-xor-nop.npy')

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

# pcc = []
# for i in range(2):
#     p = []
#     for s in range(SAMPLES):
#         core_samples_at_time = data[i][0][:, s]
#         cache_samples_at_time = data[i][1][:, s]
#
#         cr = sp.stats.pearsonr(core_samples_at_time, cache_samples_at_time).statistic
#         p.append(cr)
#     pcc.append(p)

data = averages

# model_idx, model = extract_model(data[1][0], data[0][0])
# np.save('model', model)
model = np.load('model.npy')

plt.figure(21)
plt.plot(model)

plt.figure(20)
plt.plot(sliding_window(data[0][0], model, do_y_shift = False))

for i, scope_name in enumerate(SCOPE_NAME):
    plt.figure(i)
    plt.plot(abs((data[1][i] - data[0][i])) / ITERATIONS, label = f"{EXPERIMENT[1]} - {EXPERIMENT[0]}")
    for exp_idx, experiment in enumerate(EXPERIMENT):
        plt.plot(data[exp_idx][i] / ITERATIONS, label = experiment)
    plt.title(f"{scope_name} Probe")
    plt.xlabel("Samples / Clock Cycles")
    plt.ylabel("Volts")
    plt.xlim(AVG_WINDOW, SAMPLES - AVG_WINDOW)
    plt.legend()

# for i, d in enumerate(pcc):
#     plt.figure(i+2)
#     plt.plot(d)
#     plt.title(f"Correlation Core and Cache '{experiments[i]}'")
#     plt.xlabel("Samples / Clock Cycles")
#     plt.ylabel("Pearson Correlation Coefficient")
#     # plt.ylim(-1.1, 1.1)

plt.show()