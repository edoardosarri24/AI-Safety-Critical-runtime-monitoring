#ifndef INITIAL_STATE_SAMPLER_HPP
#define INITIAL_STATE_SAMPLER_HPP

#include <random>

class InitialStateSampler {

    private:
        std::mt19937_64 random_engine_;
        std::uniform_real_distribution<double> dist_distance_;
        std::uniform_real_distribution<double> dist_velocity_leader_;
        std::uniform_real_distribution<double> dist_velocity_ego_;

    public:
        InitialStateSampler();
        double sample_distance();
        double sample_velocity_leader();
        double sample_velocity_ego();
};

#endif // INITIAL_STATE_SAMPLER_HPP