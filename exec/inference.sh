#!/bin/bash

set -e

# Variable
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Compilation
cd "$PROJECT_ROOT/src/inference"
mkdir -p build
cd build
# We build in Release mode for optimal performance during inference
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(sysctl -n hw.ncpu)

# Inference
cd "$PROJECT_ROOT"
./src/inference/build/ADAS_RTA
