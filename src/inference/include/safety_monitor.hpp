#ifndef SAFETY_MONITOR_HPP
#define SAFETY_MONITOR_HPP

#include "global_parameters.hpp"
#include <cmath>

namespace safety_monitor {

    inline constexpr double safety_monitor::safe_acceleration() {
        return physic_parameters::MIN_ACCELLERATION;
    }
    double cirtical_distance(
        double const leader_velocity,
        double const ego_velocity);

}

#endif // SAFETY_MONITOR_HPP