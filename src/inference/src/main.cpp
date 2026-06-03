#include <iostream>
#include "simulator.hpp"
#include "leader_acceleration_predictor.hpp"
#include "safety_monitor.hpp"

int main() {

    // Init
    Simulator simulator{};
    Leader_acceleration_predictor predicotor{};

    // Main cicle
    while (!simulator.is_terminated() && !simulator.is_truncated()) {

        // read from sensor.
        double ego_velocity = simulator.get_ego_velocity();
        double relative_velocity = simulator.get_relative_velocity();
        double leader_velocity = ego_velocity + relative_velocity;
        double critical_distance = safety_monitor::cirtical_distance(leader_velocity, ego_velocity);
        double actual_distance = simulator.get_distance();

        // Step
        double action = actual_distance <= critical_distance ?
            safety_monitor::safe_acceleration() :
            predicotor.predict(ego_velocity, actual_distance, relative_velocity);
        simulator.step(action);

    }

}
