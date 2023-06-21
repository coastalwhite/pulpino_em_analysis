#! /bin/sh

TARGET_DIR="./pulpino-top-level-cw305/program/target"
DIR_NAME="model"
LOCATION="rust/$DIR_NAME"
RAMS_DIR="./models/duration-tests"

rm -rf "$RAMS_DIR"
mkdir -p "$RAMS_DIR"

set -e

function generate_model_ram() {
    local name=$1

    ./insert_into_model.py "$name" "true" "false" "dur-ref.rs"
    rm -rf "$TARGET_DIR/$LOCATION"
    cp -r "target/model" "$TARGET_DIR/$LOCATION"

    pushd "$TARGET_DIR" > /dev/null
    ./compile.sh "$LOCATION"
    popd > /dev/null
    cp "$TARGET_DIR/out/$DIR_NAME" "$RAMS_DIR/$name-triggered.py"
    rm ./target/model/src/main.rs

    ./insert_into_model.py "$name" "false" "false" "dur-ref.rs"
    rm -rf "$TARGET_DIR/$LOCATION"
    cp -r "target/model" "$TARGET_DIR/$LOCATION"

    pushd "$TARGET_DIR" > /dev/null
    ./compile.sh "$LOCATION"
    popd > /dev/null
    cp "$TARGET_DIR/out/$DIR_NAME" "$RAMS_DIR/$name-untriggered.py"
    rm ./target/model/src/main.rs

    ./insert_into_model.py "$name" "false" "false" "dur-ref.rs" "false"
    rm -rf "$TARGET_DIR/$LOCATION"
    cp -r "target/model" "$TARGET_DIR/$LOCATION"

    pushd "$TARGET_DIR" > /dev/null
    ./compile.sh "$LOCATION"
    popd > /dev/null
    cp "$TARGET_DIR/out/$DIR_NAME" "$RAMS_DIR/$name-untriggered-noprologue.py"
    rm ./target/model/src/main.rs
}

for model in ./models/*.rvmdl
do
    name=$(basename "$model")
    echo "Running for '$name'..."
    generate_model_ram "${name%.rvmdl}"
done