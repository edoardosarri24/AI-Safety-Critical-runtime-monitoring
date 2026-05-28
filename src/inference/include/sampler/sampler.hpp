#ifndef SAMPLER_HPP
#define SAMPLER_HPP

#include <random>

class Sampler {

    protected:
        std::mt19937_64 random_engine_;
        explicit Sampler() noexcept;

    public:
        virtual ~Sampler() noexcept = default;
        Sampler(const Sampler&) = delete;
        Sampler& operator=(const Sampler&) = delete;

};

#endif // SAMPLER_HPP