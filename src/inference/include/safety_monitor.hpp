#ifndef SAFETY_MONITOR_HPP
#define SAFETY_MONITOR_HPP

#include "global_parameters.hpp"
#include <cmath>

namespace safety_monitor {

    double safe_acceleration();
    double cirtical_distance(double leader_velocity, double ego_velocity);

}

#endif // SAFETY_MONITOR_HPP