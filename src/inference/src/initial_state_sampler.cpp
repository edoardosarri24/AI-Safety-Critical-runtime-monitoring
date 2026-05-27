#include "initial_state_sampler.hpp"

InitialStateSampler::InitialStateSampler() :
    random_engine_(std::random_device{}()),
    dist_distance_(5.0, 20.0),
    dist_velocity_leader_(10.0, 20.0),
    dist_velocity_ego_(10.0, 20.0) {}

double InitialStateSampler::sample_distance() {
    return dist_distance_(random_engine_);
}

double InitialStateSampler::sample_velocity_leader() {
    return dist_velocity_leader_(random_engine_);
}

double InitialStateSampler::sample_velocity_ego() {
    return dist_velocity_ego_(random_engine_);
}