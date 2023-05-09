import chipwhisperer as cw

def get_scopes():
    return [
        cw.scope(sn = '50203220313038543230373132313036'), # Upper Probe (Core)
        cw.scope(sn = '50203120324136503130313134323031'), # Lower Probe (Cache)
    ]

def configure_scopes(scopes, samples):
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
        # scope.clock.adc_src = "extclk_x4"
        scope.clock.adc_src = "extclk_dir"
        scope.clock.extclk_freq = 20E6

        # scope.io.tio1 = "high_z"
        # scope.io.tio2 = "high_z"
        scope.trigger.triggers = "tio4"
        scope.io.hs2 = "disabled"

        # ensure ADC is locked:
        scope.clock.reset_adc()
        assert (scope.clock.adc_locked), "ADC failed to lock"

CORE_PROBE = 0
CACHE_PROBE = 1