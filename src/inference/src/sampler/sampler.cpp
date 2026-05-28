#include "sampler/sampler.hpp"

Sampler::Sampler() noexcept :
    random_engine_(std::random_device{}()) {}