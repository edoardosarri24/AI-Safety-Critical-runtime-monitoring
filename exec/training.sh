#!/bin/bash

set -e

# Variable
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
PYTHON_EXECUTABLE=$(uv python find)

# Compilation
cd "$PROJECT_ROOT/src/inference"
mkdir -p build
cd build
rm -rf CMakeCache.txt CMakeFiles
cmake .. -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE="$PYTHON_EXECUTABLE"
make -j$(sysctl -n hw.ncpu)

# Training
cp simulator_cpp.* "$PROJECT_ROOT/src/training/"
cd "$PROJECT_ROOT"
uv run --python "$PYTHON_EXECUTABLE" src/training/main.py