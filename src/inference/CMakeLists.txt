cmake_minimum_required(VERSION 3.21)
project(ADAS_RTA LANGUAGES CXX)

# Standard C++ configuration
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

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

# Target
add_executable(ADAS_RTA)

# Path
find_path(ONNXRUNTIME_INCLUDE_DIR NAMES onnxruntime/onnxruntime_cxx_api.h PATHS /opt/homebrew/include /usr/local/include)
find_library(ONNXRUNTIME_LIBRARY NAMES onnxruntime PATHS /opt/homebrew/lib /usr/local/lib)
if(NOT ONNXRUNTIME_INCLUDE_DIR OR NOT ONNXRUNTIME_LIBRARY)
    message(FATAL_ERROR "ONNX Runtime not found! Please install it (e.g. 'brew install onnxruntime').")
endif()

# Includes
target_include_directories(ADAS_RTA PRIVATE
    include
    ${CMAKE_CURRENT_BINARY_DIR}/include
    ${ONNXRUNTIME_INCLUDE_DIR}
)

# Sources
set(COMMON_SOURCES
    src/simulator.cpp
    src/leader_acceleration_model.cpp
    src/sampler/sampler.cpp
    src/sampler/initial_state_sampler.cpp
    src/sampler/acceleration_sampler.cpp
    src/leader_acceleration_predictor.cpp
    src/safety_monitor.cpp
    src/statistics_collector.cpp
)
target_sources(ADAS_RTA PRIVATE
    src/main.cpp
    ${COMMON_SOURCES}
)

target_link_libraries(ADAS_RTA PRIVATE ${ONNXRUNTIME_LIBRARY})

# Dependencies
find_package(pybind11 REQUIRED)
pybind11_add_module(simulator_cpp
    src/bindings.cpp
    ${COMMON_SOURCES}
)
target_include_directories(simulator_cpp PRIVATE
    include
)