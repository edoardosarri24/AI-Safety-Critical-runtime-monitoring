#ifndef STATISTICS_COLLECTOR_HPP
#define STATISTICS_COLLECTOR_HPP

#include <vector>

class StatisticsCollector {

    private:
        struct TelemetryEntry {
            double time;
            double distance;
            double critical_distance;
            double ego_velocity;
            double leader_velocity;
            double acceleration;
            bool rta_active;
        };
        int total_ticks_ = 0;
        int ai_calls_ = 0;
        int safety_monitor_calls_ = 0;
        double min_distance_ = 9999.0;
        double max_distance_ = 0.0;
        double sum_distance_ = 0.0;
        double max_ego_velocity_ = 0.0;
        double sum_ego_velocity_ = 0.0;
        double total_comfort_jerk_ = 0.0;
        double last_acceleration_ = 0.0;
        std::vector<TelemetryEntry> telemetries_;

    public:
        StatisticsCollector() noexcept = default;

        // Records a simulation step
        void record_step(
            double time,
            double distance,
            double critical_distance,
            double ego_velocity,
            double leader_velocity,
            double acceleration,
            bool rta_active);

        // Generates a PDF report in data/simulation_results.pdf
        void generate_pdf_report() const;

};

#endif // STATISTICS_COLLECTOR_HPP
