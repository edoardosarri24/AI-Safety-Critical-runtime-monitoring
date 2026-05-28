#ifndef ACCELERATION_SAMPLER_HPP
#define ACCELERATION_SAMPLER_HPP

#include "sampler/sampler.hpp"
#include <random>

class AccelerationSampler : public Sampler {

    private:
        std::uniform_real_distribution<double> dist_amplitude_;
        std::uniform_real_distribution<double> dist_omega_;
        std::uniform_real_distribution<double> dist_phi_;
        std::uniform_real_distribution<double> dist_t_brake_;
        std::uniform_real_distribution<double> dist_probability_;

    public:
        explicit AccelerationSampler() noexcept;
        double sample_amplitude() noexcept;
        double sample_omega() noexcept;
        double sample_phi() noexcept;
        double sample_t_brake() noexcept;
};

#endif // ACCELERATION_SAMPLER_HPP