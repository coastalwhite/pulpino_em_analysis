SCOPE_NAME = [
    "Core",
    "Cache",
]

TARGET_ITERATIONS = 1_000
MODEL_ITERATIONS = 1_000
CLOCK_CYCLE_LENGTH = 540
SAMPLE_4_PER_CC = True
CLK_FREQ = 20E6

if SAMPLE_4_PER_CC:
    SAMPLES_PER_CC = 4
    ADC_CLK_SRC = "extclk_x4"
else:
    SAMPLES_PER_CC = 1
    ADC_CLK_SRC = "extclk_x1"
SAMPLES = CLOCK_CYCLE_LENGTH * SAMPLES_PER_CC