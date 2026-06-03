#ifndef SIMULATOR_HPP
#define SIMULATOR_HPP

#include <vector>
#include <string>
#include "sampler/initial_state_sampler.hpp"
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
        double pre_step_ego_acceleration_;

    public:
        explicit Simulator() noexcept;
        Simulator (const Simulator&) = delete;
        Simulator& operator=(const Simulator&) = delete;
        void reset() noexcept;
        void step(const double ego_acceleration) noexcept;
        double get_ego_velocity() const noexcept {return ego_velocity_;};
        double get_distance() const noexcept {return distance_;};
        double get_relative_velocity() const noexcept {return relative_velocity_;};
        double get_time() const noexcept {return current_time_;};
        bool is_terminated() const noexcept;
        bool is_truncated() const noexcept;
        double calculate_reward(double ego_acceleration) const noexcept;

};

#endif // SIMULATOR_HPP
