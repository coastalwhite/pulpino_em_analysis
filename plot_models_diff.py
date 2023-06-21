#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from scopes import NUM_PROBES
from settings import SCOPE_NAME
from model import all_models
from analysis import extract_model, avg_traces

models = all_models()
for i, model in enumerate(models):
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

    plt.figure(i)
    plt.title(f"Model '{model.name}' difference plot")
    for i in range(NUM_PROBES):
        plt.plot(np.abs(triggered_traces[i] - untriggered_traces[i]), label = SCOPE_NAME[i])

    extracted = extract_model(
        triggered_traces[0],
        untriggered_traces[0],
        model.duration_target,
        model.duration_prologue,
        fitting_method = 2,
    )

    plt.axvspan(
        extracted.index, extracted.index + model.duration_target - 1,
        alpha=0.25,
        color='green',
        label = "Model Range",
    )
    # for i in range(NUM_PROBES):
    #     for j in range(3):
    #         extracted = extract_model(
    #             triggered_traces[i],
    #             untriggered_traces[i],
    #             model.duration_target,
    #             model.duration_prologue,
    #             fitting_method = j,
    #         )
    #     
    #         plt.axvspan(
    #             extracted.index, extracted.index + model.duration_target - 1,
    #             alpha=0.25,
    #             color=COLORS[i*3+j],
    #             label = f"{SCOPE_NAME[i]} - {TECH_NAMES[j]}",
    #         )
    plt.legend()
    plt.tight_layout()

plt.show()