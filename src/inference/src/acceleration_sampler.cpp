#include "acceleration_sampler.hpp"
#include "global_parameters.hpp"
#include <limits>

constexpr double PI = 3.14159265358979323846;

AccelerationSampler::AccelerationSampler() :
    random_engine_(std::random_device{}()),
    dist_amplitude_(1.0, 5.0),
    dist_omega_(0.1, 0.4),
    dist_phi_(0.0, 2.0 * PI),
    dist_t_brake_(5.0, 20.0),
    dist_probability_(0.0, 1.0) {}

double AccelerationSampler::sample_amplitude() {
    return dist_amplitude_(random_engine_);
}

double AccelerationSampler::sample_omega() {
    return dist_omega_(random_engine_);
}

double AccelerationSampler::sample_phi() {
    return dist_phi_(random_engine_);
}

double AccelerationSampler::sample_t_brake() {
    if (dist_probability_(random_engine_) < simulation_parameter::BRAKE_PROBABILITY) {
        return dist_t_brake_(random_engine_);
    } else {
        return std::numeric_limits<double>::infinity();
    }
}