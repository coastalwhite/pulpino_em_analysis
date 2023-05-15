from math import sqrt

import numpy as np
import numpy.typing as npt

WINDOW_START = 109 # This value is selected by trail and error.
WARN_RATIO = 0.9

class Feature:
    def __init__(
        self,
        pattern: npt.NDArray[np.float64],
        scale: np.float64,
        error_tolerance: np.float64,
    ):
        self.pattern = pattern * scale
        self.scale = scale
        self.error_tolerance = error_tolerance

    def len(self):
        return len(self.pattern)

    def measure(self, trace):
        trace = derivative(trace)
        cmeasure = []
        for i in range(len(trace) - self.len()):
            cmeasure.append(np.sqrt(np.sum(np.square(
                self.pattern - trace[i:i+self.len()]
            ))))
        cmeasure = np.array(cmeasure)
        cmax = np.max(cmeasure)

        return cmeasure / cmax

    def discrete(self, trace):
        trace = derivative(trace)
        dmeasure = []
        for i in range(len(trace) - self.len()):
            values = np.abs(self.pattern - trace[i:i+self.len()])
            in_range = [
                values[j] <= self.scale * self.error_tolerance
                for j in range(self.len())
            ]

            if all(in_range):
                dmeasure.append(1)
            else:
                dmeasure.append(0)

        return np.array(dmeasure)

class Model:
    def __init__(self, at, wave, distance) -> None:
        self.index = at
        self.wave = wave
        self.distance = distance

    def matching_wave(self, wave):
        window_size = len(self.wave)
        return wave[self.index:self.index + window_size]

def avg_traces(traces):
    return np.mean(traces, axis=0)

def compress_x4_wave(trace):
    assert len(trace) % 4 == 0

    return np.array([
        np.mean(trace[i:i+4])
        for i in range(0, len(trace), 4)
    ])

def derivative(trace):
    return np.diff(trace)

def extract_model(
    target_wave: npt.NDArray[np.float64],
    reference_wave: npt.NDArray[np.float64],
    window_size: int,
    prologue_length: int,
    fitting_method = 2,
):
    """
    Extracts the model after a clear difference between `wave1` and `wave2`.
    The model is given as an array of `window_size` elements which is `offset`
    samples after the largest difference between `wave1` and `wave2`.
    """

    assert len(target_wave) == len(reference_wave)
    wave_len = len(target_wave)
    assert window_size < wave_len

    delta_wave = np.abs(target_wave - reference_wave)

    if fitting_method == 0:
        offset = np.argmax([
            np.sum(delta_wave[i:i + window_size])
            for i in range(wave_len - window_size)
        ])
        
        interval_start = offset
        interval_end = offset + window_size
    elif fitting_method == 1:
        max_diff_idx = np.argmax(delta_wave)

        interval_start = max_diff_idx
        interval_end   = max_diff_idx + 1

        # Expand out from the max until we have a interval of length `window_size`
        while interval_end - interval_start < window_size:
            if interval_start == 0:
                interval_end += 1
                continue
            if interval_end == wave_len:
                interval_start -= 1
                continue

            if delta_wave[interval_start - 1] > delta_wave[interval_end]:
                interval_start -= 1
            else:
                interval_end += 1
    else:
        interval_start = (WINDOW_START + prologue_length)
        interval_end = interval_start + (window_size)

    # Ensure that there are no other elements that are reasonably close
    for i, v in enumerate(delta_wave):
        if i >= interval_start or i < interval_end:
            continue
        if v / max(delta_wave) < WARN_RATIO:
            continue
        
        if i < interval_start:
            offset = interval_start - i
        else:
            offset = i - interval_end
        print(f"[WARNING]: High delta at offset '{offset}' from model interval")
    
    return Model(interval_start, target_wave[interval_start:interval_end], max(delta_wave))

def sliding_window(
    trace: npt.NDArray[np.float64],
    model: npt.NDArray[np.float64],
    do_y_shift = False,
):
    """
    Calculate the square difference of between the `model` subtrace and each
    point of the `trace`. The `do_y_shift` parameter allows to compensate for a
    constant y offset in the trace / subtrace and will automatically find the
    minimum value for each subtrace matching.
    """
    window_size = len(model)
    num_values = len(trace) - window_size
    values = np.zeros(num_values)

    if do_y_shift:
        for i in range(num_values):
            subtrace = trace[i:i+window_size]
            dtrace = subtrace - model

            # V = sum j<window_size : (|a_j - b_j| + x)^2
            # Xmin = - (sum |a_j - b_j|) / (sum |a_j - b_j|^2)
            quot = np.sum(dtrace)
            div = window_size

            # Derived with the Quadratic Formula
            x_min = quot / div
            
            y = np.sum(np.square(dtrace - np.repeat(x_min, window_size)))
            
            # Normalize
            values[i] = y / window_size
    else:
        for i in range(num_values):
            # V = sum j<window_size : (a_j - b_j)^2
            v = np.sum(np.square(trace[i:i+window_size] - model))
            values[i] = v / window_size

    return values

def identify_cache_miss_pattern(cache_trace):
    cache_miss_feature = Feature(
        np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1]),
        np.float64(0.006),
        np.float64(0.004),
    )

    return (np.array([]), cache_miss_feature.discrete(cache_trace))

def sliding_windows_to_measure(
    sw0: npt.NDArray[np.float64],
    sw1: npt.NDArray[np.float64],
    offset: int,
) -> npt.NDArray[np.float64]:
    assert len(sw0) == len(sw1)
    sw_len = len(sw0)
    abs_offset = abs(offset)
    assert sw_len > abs_offset
    
    result = np.empty(sw_len)

    # Calculate measure
    for i in range(abs_offset, sw_len - abs_offset):
        v0 = sw0[i]
        v1 = sw1[i + offset]
    
        result[i] = sqrt((1 / (v0**2)) + (1 / (v1**2)))

    for i in range(abs_offset):
        result[i] = 0.0
        result[sw_len - abs_offset + i] = 0.0

    return result
