#include "statistics_collector.hpp"
#include "global_parameters.hpp"
#include <iostream>
#include <iomanip>
#include <cmath>
#include <algorithm>
#include <fstream>
#include <cstdlib>

void StatisticsCollector::record_step(
        double time,
        double distance,
        double critical_distance,
        double ego_velocity,
        double leader_velocity,
        double acceleration,
        bool rta_active) {
    // Total metrics
    total_ticks_++;
    if (rta_active) {
        safety_monitor_calls_++;
    } else {
        ai_calls_++;
    }
    // Distance metrics
    min_distance_ = std::min(min_distance_, distance);
    max_distance_ = std::max(max_distance_, distance);
    sum_distance_ += distance;
    // Velocity metrics
    max_ego_velocity_ = std::max(max_ego_velocity_, ego_velocity);
    sum_ego_velocity_ += ego_velocity;
    // Record telemetry entry
    telemetries_.push_back({
        time,
        distance,
        critical_distance,
        ego_velocity,
        leader_velocity,
        acceleration,
        rta_active
    });
    // Comfort metrics (jerk approximation: change in acceleration)
    if (total_ticks_ > 1) {
        total_comfort_jerk_ += std::abs(acceleration - last_acceleration_);
    }
    last_acceleration_ = acceleration;
}

void StatisticsCollector::generate_pdf_report() const {
    // Write temporary file.
    std::ofstream csv_file(data::RESULTS_PATH.data());
    if (!csv_file.is_open()) {
        std::cerr << "Error: Crafting the temporary file " << data::RESULTS_PATH.data() << "\n";
        return;
    }
    csv_file << "time,distance,critical_distance,ego_velocity,leader_velocity,acceleration,rta_active\n";
    for (const auto& entry : telemetries_) {
        csv_file << entry.time << ","
            << entry.distance << ","
            << entry.critical_distance << ","
            << entry.ego_velocity << ","
            << entry.leader_velocity << ","
            << entry.acceleration << ","
            << (entry.rta_active ? 1 : 0) << "\n";
    }
    csv_file.close();
    // Generation of PDF.
    std::cout << "PDF report generation...\n";
    int result = std::system("uv run src/inference/src/generate_pdf.py");
    if (result != 0) {
        std::cerr << "Error: generation PDF report. Be sure that 'uv' is installated.\n";
    } else {
        std::cout << "PDF report saved in" << data::RESULTS_PATH.data() << " \n";
    }
    // Remove temporary file
    std::remove(data::RESULTS_PATH.data());
}
