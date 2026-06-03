#include "safety_monitor.hpp"
#include "global_parameters.hpp"
#include <cmath>

constexpr double safety_monitor::safe_acceleration() {
    return physic_parameters::MIN_ACCELLERATION;
}

double safety_monitor::cirtical_distance(double const leader_velocity, double const ego_velocity) {
        return ego_velocity * simulation_parameter::dt
            + (
                (std::pow(ego_velocity,2) - std::pow(leader_velocity,2))
                /
                (2 * physic_parameters::MIN_ACCELLERATION)
            );
    }

