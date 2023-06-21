# EM Analysis

## Getting Started

To get started first run the following command. This will link in the files from
`pulpino-top-level-cw305` and lower the clock frequency to 20MHz:

```bash
./setup.sh
```

Afterwards, make sure to insert the serial numbers of the capture boards in the
`scopes.py::SERIAL_NUMBERS` array. The serial number can be gotten by
one-by-one connecting the capture boards and running `./get_serial.py 2>
/dev/null`.

## RISC-V Model (RVMDL)

This repository utilizes a file format with extension `.rvmdl` to define a
sequence of instructions that is searched for by the algorithms. These models
are defined in `./models/definitions` with a syntax illustrated by the
following listing.

```asm
# Comments can be given by starting the line with `#`

# Give cycle length for the Prologue
# Duration Prologue: 19
# Give cycle length for the Target
# Duration Target: 7

# We have to define 3 sections: Prologue, Target and Epilogue
# These are followed by a sequence of instructions that are part of that
# section.

# Prologue
lui     t3, 0x100
lui     t4, 0x101
lw		x0,0(t3)

# Target
lw      x0,0(t3)

# Epilogue
nop
```

The `rvmdl` script manages the models. It contains a few subcommands.

- `status`. Give the enable/disable status of specific models or `all` models.
- `enable`. Enable specific models or `all` models.
- `disable`. Disable specific models or `all` models.
- `show`. Show a waveform for specific models or `all` models.

Assess the correctness of the given durations in the model, there is a utility
provided. This requires the hardware to be plugged in.

```bash
source env.sh
./form_durations.sh        # Form the executables for the duration testing
./measure_for_durations.py # Measure the duration on the hardware
```

To measure the waveform and extract the area of interest. This requires the
hardware to be plugged in.

```bash
source env.sh
./form_models.sh           # Form the executables for the models
./measure_for_models.py    # Measure the waveform on the hardware
./extract_models.py        # Extract the areas of interest
```

Afterwards, the `./rvmdl show all` command should show the model waveforms for
all enabled models.

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

## Define a Target program

To define a target program, first clone the base program, then add your code. 

```bash
cd pulpino-top-level-cw305/program/target
cp -r rust/power_trace rust/new_target

# Change the `name` value in rust/new_target/Cargo.toml to `new_target`

# Insert your code into
# pulpino-top-level-cw305/program/target/rust/new_target/src/main.rs

# Compile your new target
./compile.sh rust/new_target

# Change back to the root folder
cd ../../..
# Link in the new_target as your measure program
ln -sf $PWD/pulpino-top-level-cw305/program/target/out/new_target program.py
```

Then, we can measure the emission with.

```bash
./measure.py
```

```bash

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