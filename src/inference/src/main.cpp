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
        double critical_distance = safety_monitor::cirtical_distance(leader_velocity, ego_velocity);
        double actual_distance = simulator.get_distance();

        // Control and action
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

        // Step
        simulator.step(action);
        collector.record_step(
            simulator.get_time(),
            actual_distance,
            critical_distance,
            ego_velocity,
            leader_velocity,
            action,
            rta_active);
    }

    // Result.
    if (simulator.get_distance() <= 0.0) {
        std::cout << "Result: Collision detected: distance <= 0)\n";
    } else if (simulator.get_distance() >= 50.0) {
        std::cout << "Result: Recovery necessary (Leader vehicle lost, d >= 50m)\n";
    } else {
        std::cout << "Result: Simulation completed sucessfully\n";
    }

    // Report generation.
    collector.generate_pdf_report();

    return 0;
}
