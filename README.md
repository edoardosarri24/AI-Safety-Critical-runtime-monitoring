# AI Safety Critical Runtime Monitoring
This project discuss and implements a Run-Time Assurance (RTA) system of an Artificial Intelligence (AI) based Advanced Driver Assistance System (ADAS).

You can see the report in [report.pdf](report.pdf) file.
You can see the slides in [slides.pdf](slides.pdf) file.

# Requirements
The project use both Python and C++, so the dependencies are:
- **C++17 compiler** and **CMake**.
- **ONNX Runtime**.
- **pybind11**.
- **Python** (>= 3.9)
- **uv**

# Quick Start
Follow these instructions in order to replicate the training and the inference. All commands, contained in `exec/` directory, should be executed from the project root directory.

### Step 1: Configuration
Physics and simulation parameters are configured in the C++ [src/inference/include/global_parameters.hpp](src/inference/include/global_parameters.hpp) file.

### Step 2: Training
To compile the C++ simulator with Python bindings and train the PPO agent:
```bash
./exec/training.sh
```

### Step 3: Inference
To compile and execute the inference simulation using the trained ONNX model:

##### Standard
To compile and execute the C++ inference simulation using the trained ONNX model. The results will be produce in [data](data/) directory.
```bash
./exec/inference.sh
```

##### Interactive GUI
Runs the Gymnasium environment with real-time Pygame visualization:
```bash
./exec/inference.sh [-v|--visualize]
```
Inside the GUI:
- `Space`: Pause and resume the simulation.
- `Esc`: Quit the simulation.

# Project Structure
Below is the directory and file structure of the project:

```text
.
├── exec    # Contains the script to execute the tool.
├── paper   # Paper studied.
├── report  # LaTeX source files for the the report.
├── slides  # LaTeX source files for the the slides.
└── src
    ├── inference   # Code to execute the safety-critical system.
    └── training    # Code to execute the agent training.
```
