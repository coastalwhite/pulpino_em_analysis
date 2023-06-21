#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from analysis import avg_traces

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

stddev = stddev[0]
data = data[0]

print(np.shape(data))

plt.plot(data, label = "Wave")
plt.plot(data - stddev, label = "BotWave")
plt.plot(data + stddev, label = "TopWave")
plt.legend()
plt.show()