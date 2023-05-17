# EM Analysis

## Create new model

1. Create a new file in `./models` folder.
2. Add the `# Prologue`, `# Target` and `# Epilogue` sections.
3. Add the assembly you want to use belong the titles of those sections. You can
   only use the `t3` and `t4` registers. A line started with a `#` is ignored.

```asm
# Basic Cache Miss
# Evicts a cache line and then loads it again

# Prologue
lui t3,0x100
lw  x0,0(t3)
lui t3,0x101
lw  x0,0(t3)
lui t4,0x104

# Target
lw  x0,0(t4)

# Epilogue
nop
```

## Get Model Prologue and Target durations

```bash
source env.sh
./form_durations.sh
./measure_for_durations.py
```

## Extract the models

```bash
source env.sh
./form_models.sh
./measure_for_models.py
./extract_models.py
```

## Measure Power Trace

```bash
ln -sf $PWD/pulpino-top-level-cw305/program/target/out/name_of_target program.py
./measure.py
```

## Show Traces of Models

```bash
./process.py
```