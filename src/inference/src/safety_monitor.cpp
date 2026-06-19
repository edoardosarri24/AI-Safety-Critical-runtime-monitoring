#include "safety_monitor.hpp"
#include "global_parameters.hpp"
#include <cmath>
#include <algorithm>

double safety_monitor::critical_distance(double const leader_velocity, double const ego_velocity) {
        return std::max(0.0, ego_velocity * simulation_parameter::dt
            + (
                (std::pow(ego_velocity,2) - std::pow(leader_velocity,2))
                /
                (2 * std::abs(physic_parameters::MIN_ACCELLERATION))
            ));
    }


