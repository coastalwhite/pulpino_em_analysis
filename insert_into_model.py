#! /usr/bin/env python

import sys

if len(sys.argv) < 3:
    print(f"Usage {sys.argv[0]} <name> <trigger enable>")
    exit(2)

name = sys.argv[1]
trigger_enable = sys.argv[2].strip().lower()

if trigger_enable == 'true':
    trigger_enable = True
elif trigger_enable == 'false':
    trigger_enable = False
else:
    raise Exception("[ERROR]: Invalid `trigger_enable` value. Allowed values are 'true' and 'false'")

TRIGGER_ENABLE = 'xor t2,t1,t1'
TRIGGER_DISABLE = 'nop'

TARGET_DIR = './target/model'
MODELS_DIR = './models'

def write_main_rs(prologue, target, epilogue, is_trigger_enabled):
    main_rs = open(f'{TARGET_DIR}/src/main.rs', 'w')
    ref_rs = open(f'{TARGET_DIR}/src/ref.rs', 'r')

    for line in ref_rs.readlines():
        if line.strip() == '{PROLOGUE}':
            main_rs.writelines(prologue + ['\n'])
        elif line.strip() == '{TRIGGER}':
            if is_trigger_enabled:
                main_rs.writelines([TRIGGER_ENABLE + '\n'])
            else:
                main_rs.writelines([TRIGGER_DISABLE + '\n'])
        elif line.strip() == '{TARGET}':
            main_rs.writelines(target + ['\n'])
        elif line.strip() == '{EPILOGUE}':
            main_rs.writelines(epilogue + ['\n'])
        else:
            main_rs.writelines([line])

    main_rs.close()
    ref_rs.close()
    

with open(f'{MODELS_DIR}/{name}') as model:
    lines = model.readlines()

    [prologue_start, target_start, epilogue_start] = [
        list(filter(lambda i: lines[i].strip().startswith(f'# {section_text}'), range(len(lines)))) for section_text in ['Prologue', 'Target', 'Epilogue']
    ]

    assert len(prologue_start) == 1
    assert len(target_start) == 1
    assert len(epilogue_start) == 1

    prologue_start = prologue_start[0]
    target_start = target_start[0]
    epilogue_start = epilogue_start[0]
    
    assert prologue_start < target_start
    assert target_start < epilogue_start

    prologue = lines[prologue_start+1:target_start]
    target = lines[target_start+1:epilogue_start]
    epilogue = lines[epilogue_start+1:]
    
    prologue = list(filter(lambda l: not l.strip().startswith('#'), prologue))
    target = list(filter(lambda l: not l.strip().startswith('#'), target))
    epilogue = list(filter(lambda l: not l.strip().startswith('#'), epilogue))

    write_main_rs(prologue, target, epilogue, trigger_enable)