#! /usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

from settings import SCOPE_NAME
from model import all_models

models = all_models()
for i, model in enumerate(models):
    for j in range(5):
        untriggered = np.load(f'./test_reliability/model_data/{model.name}-untriggered-{j}.npy')
        triggered = np.load(f'./test_reliability/model_data/{model.name}-triggered-{j}.npy')
        model_waveform = np.load(f'./test_reliability/model_data/{model.name}-model-{j}.npy')

        for k in range(2):
            plt.figure(i*10 + k)
            plt.plot(model_waveform[k], label = f"{j}")

    for j in range(2):
        plt.figure(i*10 + j)
        plt.legend()
        plt.title(f"{model.name} - {SCOPE_NAME[j]}")
    
plt.show()