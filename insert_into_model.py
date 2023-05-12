#! /usr/bin/env python
# Inserts the assembly of a model into a reference file.

import sys
from model import ModelFile

if len(sys.argv) < 3:
    print(f"Usage {sys.argv[0]} <name> <trigger enable> [use nops as replacement] [reference file] [insert prologue]")
    exit(2)

def bool_lit_parse(s: str) -> bool:
    if s == 'true':
        return True
    elif s == 'false':
        return False
    else:
        raise Exception("[ERROR]: Invalid bool value. Allowed values are 'true' and 'false'")

name = sys.argv[1]
trigger_enable = bool_lit_parse(sys.argv[2].strip().lower())

use_nops_as_replacement = True
if len(sys.argv) >= 4:
    use_nops_as_replacement = bool_lit_parse(sys.argv[3].strip().lower())

insert_prologue = True
if len(sys.argv) >= 6:
    insert_prologue = bool_lit_parse(sys.argv[5].strip().lower())

TARGET_DIR = './target/model'
REFERENCE_FILE = 'ref.rs'

if len(sys.argv) >= 5:
    REFERENCE_FILE = sys.argv[4]

def write_main_rs(
    prologue: list[str],
    target: list[str],
    epilogue: list[str],
    target_num_clock_cycles: int,
    is_trigger_enabled: bool,
    use_nops_as_replacement: bool,
    insert_prologue: bool,
):
    main_rs = open(f'{TARGET_DIR}/src/main.rs', 'w')
    ref_rs = open(f'{TARGET_DIR}/src/{REFERENCE_FILE}', 'r')

    for line in ref_rs.readlines():
        if line.strip() == '{PROLOGUE}':
            if insert_prologue:
                main_rs.writelines(prologue + ['\n'])
        elif line.strip() == '{TARGET}':
            if is_trigger_enabled:
                main_rs.writelines(target + ['\n'])
            elif use_nops_as_replacement:
                main_rs.writelines(['nop\n' for _ in range(target_num_clock_cycles)])
        elif line.strip() == '{EPILOGUE}':
            main_rs.writelines(epilogue + ['\n'])
        else:
            main_rs.writelines([line])

    main_rs.close()
    ref_rs.close()

model = ModelFile(name)
write_main_rs(
    model.prologue, model.target, model.epilogue,
    model.duration_target, trigger_enable, use_nops_as_replacement,
    insert_prologue,
)