#! /usr/bin/env python

from os import listdir
from os.path import isfile, join

import numpy as np
from tqdm import trange
from scopes import configure_scopes, get_scopes
from connection import PulpinoConnection

from typing import Tuple
from model import all_models, ModelFile

MODELS_PATH = './models'

def get_duration(pulpino, ram):
    # Reset the PULPINO
    pulpino.reset()

    # Program the RAM address at an offset of 0x0
    pulpino.program(0x0, ram)

    # Stop Programming
    pulpino.stop_programming()

    # Entry Address
    pulpino.send_word(0x0)

    return pulpino.receive_word()

bitpath = "./set_associative_cache.bit"
pulpino = PulpinoConnection(bitpath, scope = None, force = True)

if not pulpino.get_raw().fpga.isFPGAProgrammed():
    print("ERR: FPGA failed to program")
    exit(1)

durations: list[Tuple[ModelFile, int, int]] = []
models = all_models()
for model in models:
    untriggered_ram = __import__(f"{model.name}-untriggered")
    untriggered_ram = untriggered_ram.RAM

    untriggered_np_ram = __import__(f"{model.name}-untriggered-noprologue")
    untriggered_np_ram = untriggered_np_ram.RAM

    triggered_ram = __import__(f"{model.name}-triggered")
    triggered_ram = triggered_ram.RAM

    print(f"Running for model '{model.name}'...")

    untriggered_duration = get_duration(pulpino, untriggered_ram)
    untriggered_np_duration = get_duration(pulpino, untriggered_np_ram)
    triggered_duration = get_duration(pulpino, triggered_ram)

    assert triggered_duration > untriggered_duration
    assert untriggered_duration > untriggered_np_duration
    target_duration = triggered_duration - untriggered_duration
    prologue_duration = untriggered_duration - untriggered_np_duration
    
    durations.append((model, target_duration, prologue_duration))

print('')
print('')
print('Durations')
for model, target_duration, prologue_duration in durations:
    target_correct = model.duration_target == target_duration
    prologue_correct = model.duration_prologue == prologue_duration

    print(f"{model.name}: {target_duration} (+{prologue_duration} prologue) clock cycles")
    print(f"    Prologue Correct: {prologue_correct}")
    print(f"    Target Correct: {target_correct}")