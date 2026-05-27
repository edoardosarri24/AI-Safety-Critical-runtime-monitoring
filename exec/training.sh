#!/bin/bash

# Interrompe lo script in caso di errori
set -e

# Salva la root del progetto
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)

echo "=== 1. Sincronizzazione ambiente Python ==="
cd "$PROJECT_ROOT"
# Assicura che la cartella .venv sia creata e aggiornata
uv sync

# Trova il percorso di pybind11 dentro l'ambiente virtuale di uv
PYBIND11_DIR=$(uv run python -c "import pybind11; print(pybind11.get_cmake_dir())")
echo "Trovato pybind11 in: $PYBIND11_DIR"

echo "=== 2. Compilazione del modulo C++ (pybind11) ==="
cd "$PROJECT_ROOT/src/inference"

# Crea la cartella di build se non esiste
mkdir -p build
cd build

# Configura passando il path corretto a CMake e compila
cmake .. -DCMAKE_BUILD_TYPE=Release -Dpybind11_DIR="$PYBIND11_DIR"
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu)

echo "=== 3. Posizionamento del modulo compilato in src/training ==="
cp simulator_cpp.* "$PROJECT_ROOT/src/training/"

echo "=== 4. Avvio del Training ==="
cd "$PROJECT_ROOT"
uv run src/training/main.py