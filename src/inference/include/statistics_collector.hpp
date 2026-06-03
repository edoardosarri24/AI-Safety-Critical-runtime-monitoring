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
        // Generates a PDF report.
        void generate_pdf_report() const;

};

#endif // STATISTICS_COLLECTOR_HPP
