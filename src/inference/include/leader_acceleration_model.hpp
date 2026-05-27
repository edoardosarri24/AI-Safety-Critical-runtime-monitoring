#ifndef LEADER_ACCELERATION_MODEL_HPP
#define LEADER_ACCELERATION_MODEL_HPP

#include "acceleration_sampler.hpp"

class LeaderAccelerationModel {

    private:
        AccelerationSampler sampler_;

        // Episode-specific parameters
        double current_A_;
        double current_omega_;
        double current_phi_;
        double current_t_brake_;

    public:
        LeaderAccelerationModel();
        void reset();
        double get_acceleration(double time, double leader_velocity) const;
};

#endif // LEADER_ACCELERATION_MODEL_HPP