#! /bin/sh

set -e

rm -rf model_data
mkdir -p model_data

pushd .. > /dev/null
./form_models.sh

for i in $(seq 0 4)
do
    PYTHONPATH="$PYTHONPATH:$PWD/models/rams" ./measure_for_models.py
    ./extract_models.py

    for model in ./models/*
    do
        if [ ! -f "$model" ]; then
            continue
        fi
        
        name=$(basename "$model")

        cp "./models/raw_data/$name-untriggered.npy" "./test_reliability/model_data/$name-untriggered-$i.npy" 
        cp "./models/raw_data/$name-triggered.npy" "./test_reliability/model_data/$name-triggered-$i.npy" 
        cp "./models/model_traces/$name.npy" "./test_reliability/model_data/$name-model-$i.npy" 
    done
done

popd > /dev/null