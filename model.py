from os import listdir
from os.path import isfile, islink, join

import numpy as np
import numpy.typing as npt

from scopes import NUM_PROBES

MODELS_PATH = './models'
TRIGGERED_SUFFIX = '-triggered'
UNTRIGGERED_SUFFIX = '-untriggered'

class ModelWaveForm:
    def __init__(self, waveforms: npt.NDArray[np.float64], probe_offset: int) -> None:
        self.waveforms = waveforms
        self.probe_offset = probe_offset

    def len(self) -> int:
        return len(self.waveforms[0])

class ModelFile:
    def __init__(
        self,
        name: str
    ) -> None:
        with open(f'./models/definitions/{name}.rvmdl', 'r') as f:
            lines = f.readlines()

        prologue_start = [
                prologue_start,
                target_start,
                epilogue_start,
                prologue_clock_cycles_line,
                target_clock_cycles_line
            ] = [
                list(filter(
                    lambda i: lines[i].strip().startswith(f'# {section_text}'),
                    range(len(lines))
                )) for section_text in ['Prologue', 'Target', 'Epilogue', 'Duration Prologue:', 'Duration Target:']
            ]

        # Make sure that there is only a single match
        if len(prologue_start) < 1: raise Exception("No `Prologue` section")
        if len(prologue_start) > 1: raise Exception("Multiple `Prologue` sections")
        if len(target_start) < 1: raise Exception("No `Target` section")
        if len(target_start) > 1: raise Exception("Multiple `Target` sections")
        if len(epilogue_start) < 1: raise Exception("No `Epilogue` section")
        if len(epilogue_start) > 1: raise Exception("Multiple `Epilogue` sections")
        if len(prologue_clock_cycles_line) < 1: raise Exception("No `Duration Prologue` given")
        if len(prologue_clock_cycles_line) > 1: raise Exception("Multiple `Duration Prologue` definitions")
        if len(target_clock_cycles_line) < 1: raise Exception("No `Duration Target` given")
        if len(target_clock_cycles_line) > 1: raise Exception("Multiple `Duration Target` definitions")
            
        prologue_start = prologue_start[0]
        target_start = target_start[0]
        epilogue_start = epilogue_start[0]
        target_clock_cycles_line = target_clock_cycles_line[0]
        prologue_clock_cycles_line = prologue_clock_cycles_line[0]

        in_correct_order = [
            prologue_clock_cycles_line < target_clock_cycles_line,
            target_clock_cycles_line < prologue_start,
            prologue_start < target_start,
            target_start < epilogue_start,
        ]

        # Make sure that the order of the sections in the file is correct
        if not all(in_correct_order):
            raise Exception("Invalid order of sections and definitions")

        prologue_clock_cycles = lines[prologue_clock_cycles_line]
        prologue_clock_cycles = prologue_clock_cycles[prologue_clock_cycles.find(':')+1:]
        prologue_clock_cycles = prologue_clock_cycles.strip()
        prologue_clock_cycles = int(prologue_clock_cycles)

        target_clock_cycles = lines[target_clock_cycles_line]
        target_clock_cycles = target_clock_cycles[target_clock_cycles.find(':')+1:]
        target_clock_cycles = target_clock_cycles.strip()
        target_clock_cycles = int(target_clock_cycles)
        
        prologue = lines[prologue_start+1:target_start]
        target = lines[target_start+1:epilogue_start]
        epilogue = lines[epilogue_start+1:]
        
        # Remove comments
        prologue = list(filter(lambda l: not l.strip().startswith('#'), prologue))
        target = list(filter(lambda l: not l.strip().startswith('#'), target))
        epilogue = list(filter(lambda l: not l.strip().startswith('#'), epilogue))

        self.name = name
        self.duration_prologue = prologue_clock_cycles
        self.duration_target = target_clock_cycles
        self.prologue = prologue
        self.target = target
        self.epilogue = epilogue
    
    def load_triggered_trace(self) -> npt.NDArray[np.float64]:
        return np.load(f'{MODELS_PATH}/raw_data/{self.name}{TRIGGERED_SUFFIX}.npy')
    
    def load_untriggered_trace(self) -> npt.NDArray[np.float64]:
        return np.load(f'{MODELS_PATH}/raw_data/{self.name}{UNTRIGGERED_SUFFIX}.npy')
    
    def save_triggered_trace(self, probe_data: npt.NDArray[np.float64]):
        np.save(f'{MODELS_PATH}/raw_data/{self.name}{TRIGGERED_SUFFIX}', probe_data)
    
    def save_untriggered_trace(self, probe_data: npt.NDArray[np.float64]):
        np.save(f'{MODELS_PATH}/raw_data/{self.name}{UNTRIGGERED_SUFFIX}', probe_data)

    def load_waveform(self) -> ModelWaveForm:
        model_traces = np.load(f'{MODELS_PATH}/model_traces/{self.name}.npy')
        probe_offset = int(round(model_traces[len(model_traces)-1][0]))
        
        return ModelWaveForm(model_traces[:2], probe_offset)

    def save_waveform(self, waveform: ModelWaveForm):
        print(f"Length: {waveform.len()}")
        traces = [
            waveform.waveforms[i] for i in range(NUM_PROBES)
        ]
        traces.append(
            np.array([waveform.probe_offset for _ in range(waveform.len())]).astype(np.float64),
        )
        traces = np.array(traces)

        np.save(f'{MODELS_PATH}/model_traces/{self.name}', traces)

def all_models() -> list[ModelFile]:
    all_files = [
        f for f in listdir(MODELS_PATH)
        if islink(join(MODELS_PATH, f))
    ]
    all_rvmdl_files = list(filter(lambda f: f.endswith('.rvmdl'), all_files))
    return [ModelFile(f[:-len('.rvmdl')]) for f in all_rvmdl_files]