import chipwhisperer as cw
import numpy as np

from tqdm import trange

from analysis import compress_x4_wave
from connection import PULPINO_CLK_FREQ, PulpinoConnection
from settings import ADC_CLK_SRC, CLK_FREQ, SAMPLE_4_PER_CC, SAMPLES_PER_CC

def get_scopes():
    return [
        cw.scope(sn = '50203220313038543230373132313036'), # Upper Probe (Core)
        cw.scope(sn = '50203120324136503130313134323031'), # Lower Probe (Cache)
    ]

def configure_scopes(scopes, samples: int):
    assert PULPINO_CLK_FREQ == CLK_FREQ

    for scope in scopes:
        scope.gain.db = 30
        scope.gain.gain = 60
        scope.gain.mode = "high"

        scope.adc.samples = samples
        scope.adc.offset = 0
        scope.adc.basic_mode = "rising_edge"
        scope.adc.timeout = 2

        scope.clock.clkgen_src = "extclk"
        scope.clock.freq_ctr_src = "extclk"
        scope.clock.adc_src = f"{ADC_CLK_SRC}"
        scope.clock.extclk_freq = CLK_FREQ

        scope.trigger.triggers = "tio4"
        scope.io.hs2 = "disabled"

        # ensure ADC is locked:
        scope.clock.reset_adc()
        assert (scope.clock.adc_locked), "ADC failed to lock"

def capture_traces(scopes, pulpino: PulpinoConnection, ram: list[int], num_traces: int, samples: int):
    configure_scopes(scopes, samples)

    # Reset the PULPINO
    pulpino.reset()

    # Program the RAM address at an offset of 0x0
    pulpino.program(0x0, ram)

    # Stop Programming
    pulpino.stop_programming()

    # Entry Address
    pulpino.send_word(0x0)

    assert samples % SAMPLES_PER_CC == 0

    probe_waveforms = [
        np.empty((num_traces, int(samples / SAMPLES_PER_CC)), dtype=np.float64),
        np.empty((num_traces, int(samples / SAMPLES_PER_CC)), dtype=np.float64),
    ]

    for j in trange(num_traces):
        for scope in scopes:
            scope.arm()

        pulpino.send_byte(0)

        for i, scope in enumerate(scopes):
            ret = scope.capture()

            if ret:
                print("Failed to capture")
                exit(1)

            wave = scope.get_last_trace()
            
            if not isinstance(wave, np.ndarray):
                print("[ERROR]: Invalid array type")
                exit(1)

            wave = wave.astype(np.float64, copy=False)
            if SAMPLE_4_PER_CC:
                wave = compress_x4_wave(wave)

            probe_waveforms[i][j] = wave
    
    return np.array(probe_waveforms)

CORE_PROBE = 0
CACHE_PROBE = 1
NUM_PROBES = 2