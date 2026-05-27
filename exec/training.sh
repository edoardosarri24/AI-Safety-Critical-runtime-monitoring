#!/bin/bash

# Interrompe lo script in caso di errori
set -e

# Salva la root del progetto
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)

# Chiediamo a uv di trovare il vero Python di sviluppo installato sul sistema
PYTHON_EXECUTABLE=$(uv python find)
echo "=== Usando Python trovato da uv: $PYTHON_EXECUTABLE ==="

echo "=== 1. Compilazione del modulo C++ (pybind11) ==="
cd "$PROJECT_ROOT/src/inference"

# Crea la cartella di build se non esiste ed entra
mkdir -p build
cd build

# Svuota la cache precedente per riconfigurare la versione corretta di Python
rm -rf CMakeCache.txt CMakeFiles

# Configura passando il path di Python trovato da uv
cmake .. -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE="$PYTHON_EXECUTABLE"
make -j$(sysctl -n hw.ncpu)

echo "=== 2. Posizionamento del modulo compilato in src/training ==="
cp simulator_cpp.* "$PROJECT_ROOT/src/training/"

echo "=== 3. Avvio del Training ==="
cd "$PROJECT_ROOT"

# Usiamo uv run forzando l'uso dell'interprete 3.12 appena usato da CMake.
# uv leggerà i pacchetti (torch, stable_baselines3) dai metadati in cima a main.py
# e li caricherà al volo senza attivare o creare ambienti permanenti nella shell.
uv run --python "$PYTHON_EXECUTABLE" src/training/main.py