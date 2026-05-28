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

# Includes
target_include_directories(ADAS_RTA PRIVATE
    include
    ${CMAKE_CURRENT_BINARY_DIR}/include
)

# Sources
set(COMMON_SOURCES
    src/simulator.cpp
    src/leader_acceleration_model.cpp
    src/sampler/sampler.cpp
    src/sampler/initial_state_sampler.cpp
    src/sampler/acceleration_sampler.cpp
)
target_sources(ADAS_RTA PRIVATE
    src/main.cpp
    ${COMMON_SOURCES}
)

# Dependencies
find_package(pybind11 REQUIRED)
pybind11_add_module(simulator_cpp
    src/bindings.cpp
    ${COMMON_SOURCES}
)
target_include_directories(simulator_cpp PRIVATE
    include
)