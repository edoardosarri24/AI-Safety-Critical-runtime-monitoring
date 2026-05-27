#include "leader_acceleration_model.hpp"
#include "global_parameters.hpp"
#include <cmath>
#include <algorithm>

LeaderAccelerationModel::LeaderAccelerationModel() :
    sampler_(),
    current_A_(0.0),
    current_omega_(0.0),
    current_phi_(0.0),
    current_t_brake_(0.0) {
        reset();
    }

void LeaderAccelerationModel::reset() {
    current_A_ = sampler_.sample_amplitude();
    current_omega_ = sampler_.sample_omega();
    current_phi_ = sampler_.sample_phi();
    current_t_brake_ = sampler_.sample_t_brake();
}

double LeaderAccelerationModel::get_acceleration(double time, double leader_velocity) const {
    if (time < current_t_brake_) {
        // Calculate raw sine wave
        double raw_acceleration = current_A_ * std::sin(current_omega_ * time + current_phi_);
        return std::clamp(raw_acceleration, phisic_parameters::MIN_ACCELLERATION, phisic_parameters::MAX_ACCELLERATION);
    } else if (time >= current_t_brake_ && leader_velocity > 0.0) {
        // Maximum braking force applied
        return phisic_parameters::MAX_BRAKE;
    } else {
        // Vehicle is stopped or other condition
        return 0.0;
    }
}
