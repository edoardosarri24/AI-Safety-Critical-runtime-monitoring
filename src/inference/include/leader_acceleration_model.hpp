#ifndef LEADER_ACCELERATION_MODEL_HPP
#define LEADER_ACCELERATION_MODEL_HPP

#include "sampler/acceleration_sampler.hpp"

class LeaderAccelerationModel {

    private:
        AccelerationSampler sampler_;
        // Current-Episode parameters
        double current_A_;
        double current_omega_;
        double current_phi_;
        double current_t_brake_;

    public:
        explicit LeaderAccelerationModel() noexcept;
        void reset() noexcept;
        double get_acceleration(double time, double leader_velocity) const noexcept;
};

#endif // LEADER_ACCELERATION_MODEL_HPP