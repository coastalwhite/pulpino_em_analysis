import numpy as np

WARN_RATIO = 0.9

class Model:
    def __init__(self, at, wave, distance) -> None:
        self.index = at
        self.wave = wave
        self.distance = distance

    def matching_wave(self, wave):
        window_size = len(self.wave)
        return wave[self.index:self.index + window_size]

def extract_model(wave1, wave2, offset = 1, window_size = 5):
    """
    Extracts the model after a clear difference between `wave1` and `wave2`.
    The model is given as an array of `window_size` elements which is `offset`
    samples after the largest difference between `wave1` and `wave2`.
    """
    delta_wave = np.abs(wave2 - wave1)
    max_diff_idx = np.argmax(delta_wave)
    
    # See whether the maximum difference is not out of bounds
    if max_diff_idx > len(wave1) - window_size - offset - 1:
        raise Exception("Model index is out of range")

    # Ensure that there are no other elements that are reasonably close
    for i, v in enumerate(delta_wave):
        if i == max_diff_idx:
            continue
        if v / delta_wave[max_diff_idx] < WARN_RATIO:
            continue
        
        print(f"[WARNING]: High delta at offset '{max_diff_idx - i}' from highest delta")

    model_idx = max_diff_idx + offset
    avg_wave = (wave1 + wave2) / 2

    return Model(model_idx, avg_wave, delta_wave[max_diff_idx])

def sliding_window(trace, model, do_y_shift = False):
    """
    Calculate the square difference of between the `model` subtrace and each
    point of the `trace`. The `do_y_shift` parameter allows to compensate for a
    constant y offset in the trace / subtrace and will automatically find the
    minimum value for each subtrace matching.
    """
    window_size = len(model)
    num_values = len(trace) - window_size
    values = np.zeros(num_values)

    for i in range(num_values):
        if do_y_shift:
            # V = sum j<window_size : (|a_j - b_j| + min_y_shift)^2
            # Calculated from basic quadratic formula
            # min_y_shift = -b / 2a = (2 * sum k<window_size : |a_k - b_k|) / (2 * window_size)
            min_y_shift = np.sum(np.abs(trace[i:i+window_size] - model) / (-1 * window_size))
            values[i] = np.sum([np.square(np.abs(trace[i+j] - model[j]) + min_y_shift) for j in range(window_size)])
        else:
            # V = sum j<window_size : (a_j - b_j)^2
            v = np.sum(np.square(trace[i:i+window_size] - model))
            values[i] = v

    return values
