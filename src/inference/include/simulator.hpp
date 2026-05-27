#ifndef SIMULATOR_HPP
#define SIMULATOR_HPP

#include <vector>
#include <string>
#include "initial_state_sampler.hpp"
#include "leader_acceleration_model.hpp"

class Simulator {

    private:
        double ego_velocity_;
        double distance_;
        double relative_velocity_;
        InitialStateSampler state_sampler_;
        double current_time_;
        LeaderAccelerationModel leader_model_;
        double previus_ego_accelation_;

    public:
        Simulator();
        void reset();
        void step(const double ego_acceleration);
        double get_ego_velocity_() const {return ego_velocity_;};
        double get_distance_() const {return distance_;};
        double get_relative_velocity_() const {return relative_velocity_;};
        bool is_terminated() const;
        bool is_truncated() const;
        double calculate_reward(double ego_acceleration) const;

};

#endif // SIMULATOR_HPP
