#ifndef SAFETY_MONITOR_HPP
#define SAFETY_MONITOR_HPP

#include "global_parameters.hpp"
#include <cmath>

namespace safety_monitor {

    constexpr double safe_acceleration();
    double cirtical_distance(
        double const leader_velocity,
        double const ego_velocity);

}

#endif // SAFETY_MONITOR_HPP