#include "sampler/initial_state_sampler.hpp"

InitialStateSampler::InitialStateSampler() noexcept :
    dist_distance_(5.0, 20.0),
    dist_velocity_leader_(10.0, 20.0),
    dist_velocity_ego_(10.0, 20.0) {}

double InitialStateSampler::sample_distance() noexcept {
    return dist_distance_(random_engine_);
}

double InitialStateSampler::sample_velocity_leader() noexcept {
    return dist_velocity_leader_(random_engine_);
}

double InitialStateSampler::sample_velocity_ego() noexcept {
    return dist_velocity_ego_(random_engine_);
}