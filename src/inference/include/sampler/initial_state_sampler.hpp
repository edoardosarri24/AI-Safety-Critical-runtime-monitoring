#ifndef INITIAL_STATE_SAMPLER_HPP
#define INITIAL_STATE_SAMPLER_HPP

#include "sampler/sampler.hpp"
#include <random>

class InitialStateSampler : public Sampler {

    private:
        std::uniform_real_distribution<double> dist_distance_;
        std::uniform_real_distribution<double> dist_velocity_leader_;
        std::uniform_real_distribution<double> dist_velocity_ego_;

    public:
        explicit InitialStateSampler() noexcept;
        InitialStateSampler (const InitialStateSampler&) = delete;
        InitialStateSampler& operator=(const InitialStateSampler&) = delete;
        double sample_distance() noexcept;
        double sample_velocity_leader() noexcept;
        double sample_velocity_ego() noexcept;
};

#endif // INITIAL_STATE_SAMPLER_HPP