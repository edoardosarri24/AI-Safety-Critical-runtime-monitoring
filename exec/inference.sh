#!/bin/bash

set -e

# Variable
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Parse arguments
VISUALIZE=false
for arg in "$@"; do
    if [ "$arg" = "--visualize" ] || [ "$arg" = "-v" ]; then
        VISUALIZE=true
    fi
done

# Compilation
PYTHON_EXECUTABLE=$(uv python find)
cd "$PROJECT_ROOT/src/inference"
mkdir -p build
cd build
rm -rf CMakeCache.txt CMakeFiles
cmake .. -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE="$PYTHON_EXECUTABLE"
make -j$(sysctl -n hw.ncpu)

# Run inference
cd "$PROJECT_ROOT"
if [ "$VISUALIZE" = true ]; then
    cp src/inference/build/simulator_cpp.* "$PROJECT_ROOT/src/training/"
    uv run --python "$PYTHON_EXECUTABLE" src/inference/src/inference.py
else
    ./src/inference/build/ADAS_RTA
fi
