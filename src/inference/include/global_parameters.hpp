#ifndef HYPER_PARAMETERS_HPP
#define HYPER_PARAMETERS_HPP

#include <cstddef>

namespace simulation_parameter {
    constexpr double dt = 0.1;
    constexpr double BRAKE_PROBABILITY = 0.3;
    constexpr double MAX_TIME = 30.0;
    constexpr double TARGET_DISTANCE = 10.0;
    constexpr double MAX_DISTANCE = 50.0;
    constexpr double ALPHA = 1;
    constexpr double BETA = 0.9;
}

namespace phisic_parameters {
    constexpr double MAX_ACCELLERATION = 3.0;
    constexpr double MIN_ACCELLERATION = -8.0;
    constexpr double MAX_BRAKE = -8.0;
}

#endif // HYPER_PARAMETERS_HPP
