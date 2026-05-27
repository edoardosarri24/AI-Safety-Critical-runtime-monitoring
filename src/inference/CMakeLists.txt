cmake_minimum_required(VERSION 3.21)
project(ADAS_RTA LANGUAGES CXX)

# Standard C++ configuration
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Package
find_package(pybind11 REQUIRED)

# Flags
add_compile_options(-Wall -Wextra -Wpedantic -Wconversion -Wno-unused-parameter -Wno-long-long -Wno-pedantic)

# Optimizing in link phase
include(CheckIPOSupported)
check_ipo_supported(RESULT lto_supported OUTPUT error)
if(lto_supported)
    message(STATUS "LTO (Link Time Optimization) is enabled.")
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
else()
    message(WARNING "LTO not supported: ${error}")
endif()

# --- DEFINIZIONE TARGET ESEGUIBILE C++ ---
add_executable(ADAS_RTA)

# Includes
target_include_directories(ADAS_RTA PRIVATE
    include
    ${CMAKE_CURRENT_BINARY_DIR}/include
)

# Sources for executable
target_sources(ADAS_RTA PRIVATE
    src/main.cpp
    src/simulator.cpp
    src/acceleration_sampler.cpp
    src/initial_state_sampler.cpp
    src/leader_acceleration_model.cpp
)

# --- DEFINIZIONE TARGET MODULO PYTHON (BINDING) ---
# RIMOSSO 'PRIVATE' DA QUI SOTTO
pybind11_add_module(simulator_cpp
    src/bindings.cpp
    src/simulator.cpp
    src/initial_state_sampler.cpp
    src/leader_acceleration_model.cpp
    src/acceleration_sampler.cpp
)

target_include_directories(simulator_cpp PRIVATE
    include
)