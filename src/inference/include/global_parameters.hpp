#ifndef HYPER_PARAMETERS_HPP
#define HYPER_PARAMETERS_HPP

#include <cstddef>

namespace simulation_parameter {
    inline constexpr double dt = 0.1;
    inline constexpr double BRAKE_PROBABILITY = 0.3;
    inline constexpr double MAX_TIME = 30.0;
    inline constexpr double TARGET_DISTANCE = 10.0;
    inline constexpr double MAX_DISTANCE = 50.0;
    inline constexpr double ALPHA = 1;
    inline constexpr double BETA = 0.9;
}

namespace physic_parameters {
    inline constexpr double MAX_ACCELLERATION = 3.0;
    inline constexpr double MIN_ACCELLERATION = -8.0;
    inline constexpr double MAX_BRAKE = -8.0;
}

#endif // HYPER_PARAMETERS_HPP
