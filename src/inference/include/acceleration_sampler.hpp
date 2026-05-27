#ifndef ACCELERATION_SAMPLER_HPP
#define ACCELERATION_SAMPLER_HPP

#include <random>

class AccelerationSampler {

    private:
        std::mt19937_64 random_engine_;
        std::uniform_real_distribution<double> dist_amplitude_;
        std::uniform_real_distribution<double> dist_omega_;
        std::uniform_real_distribution<double> dist_phi_;
        std::uniform_real_distribution<double> dist_t_brake_;
        std::uniform_real_distribution<double> dist_probability_;

    public:
        AccelerationSampler();
        double sample_amplitude();
        double sample_omega();
        double sample_phi();
        double sample_t_brake();
};

#endif // ACCELERATION_SAMPLER_HPP