#include <iostream>
#include <iomanip>
#include "simulator.hpp"
#include "leader_acceleration_predictor.hpp"
#include "safety_monitor.hpp"
#include "statistics_collector.hpp"

int main() {
    // Init
    Simulator simulator{};
    simulator.reset();
    Leader_acceleration_predictor predictor{};
    StatisticsCollector collector{};

    // Main loop.
    while (!simulator.is_terminated() && !simulator.is_truncated()) {

        // Reading sensor.
        double ego_velocity = simulator.get_ego_velocity();
        double relative_velocity = simulator.get_relative_velocity();
        double leader_velocity = ego_velocity + relative_velocity;
        double critical_distance = safety_monitor::critical_distance(leader_velocity, ego_velocity);
        double actual_distance = simulator.get_distance();

        // Control and next action
        bool rta_active = (actual_distance <= critical_distance);
        double action = 0.0;
        if (rta_active) {
            action = safety_monitor::safe_acceleration();
        } else {
            action = static_cast<double>(predictor.predict(
                static_cast<float>(ego_velocity),
                static_cast<float>(actual_distance),
                static_cast<float>(relative_velocity)
            ));
        }
        simulator.step(action);

        // Collection
        double post_ego_velocity = simulator.get_ego_velocity();
        double post_relative_velocity = simulator.get_relative_velocity();
        double post_leader_velocity = post_ego_velocity + post_relative_velocity;
        double post_critical_distance = safety_monitor::critical_distance(post_leader_velocity, post_ego_velocity);

        collector.record_step(
            simulator.get_time(),
            simulator.get_distance(),
            post_critical_distance,
            post_ego_velocity,
            post_leader_velocity,
            action,
            rta_active);
    }
    
    // Results.
    collector.generate_pdf_report();
    return 0;

}
