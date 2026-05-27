#include "simulator.hpp"
#include "global_parameters.hpp"

Simulator::Simulator() :
        state_sampler_(),
        current_time_(0.0),
        leader_model_(),
        previus_ego_accelation_(0.0) {
                ego_velocity_ = state_sampler_.sample_velocity_ego();
                distance_ = state_sampler_.sample_distance();
                double initial_velocity_leader = state_sampler_.sample_velocity_leader();
                relative_velocity_ = initial_velocity_leader - ego_velocity_;
        };

void Simulator::reset() {
        ego_velocity_ = state_sampler_.sample_velocity_ego();
                distance_ = state_sampler_.sample_distance();
                double initial_velocity_leader = state_sampler_.sample_velocity_leader();
                relative_velocity_ = initial_velocity_leader - ego_velocity_;
        current_time_ = 0.0;
        leader_model_.reset();
        previus_ego_accelation_ = 0.0;
}

void Simulator::step(const double ego_acceleration) {
        // Calcolus
        double dt = simulation_parameter::dt;
        double old_leader_velocity = ego_velocity_ + relative_velocity_;
        double old_leader_acceleration = leader_model_.get_acceleration(current_time_, old_leader_velocity);
        double new_ego_velocity = std::max(0.0, ego_velocity_ + ego_acceleration * dt);
        double new_leader_velocity = std::max(0.0, old_leader_velocity + old_leader_acceleration * dt);
        double new_distance = distance_ + relative_velocity_ * dt;
        // Update
        ego_velocity_ = new_ego_velocity;
        distance_ = std::max(0.0, new_distance);
        relative_velocity_ = new_leader_velocity - new_ego_velocity;
        current_time_ += dt;
        previus_ego_accelation_ = ego_acceleration;
}

bool Simulator::is_terminated() const {
        return distance_ <= 0.0;
}

bool Simulator::is_truncated() const {
        return current_time_ >= simulation_parameter::MAX_TIME;
}

double Simulator::calculate_reward(double ego_acceleration) const {
        double leader_velocity = ego_velocity_ + relative_velocity_;
        double critical_distance = ego_velocity_ * simulation_parameter::dt + (std::pow(ego_velocity_,2)-std::pow(leader_velocity,2)) / (2*phisic_parameters::MAX_BRAKE);
        if (distance_ <= 0 || distance_ >= simulation_parameter::MAX_DISTANCE)
                return - 1000;
        double distance_from_target = std::abs(distance_ - simulation_parameter::TARGET_DISTANCE);
        double distance_reward = - simulation_parameter::ALPHA * distance_from_target;
        double ego_accelaration_distance = std::abs(previus_ego_accelation_ - ego_acceleration);
        double comfort_reward = - simulation_parameter::BETA * ego_accelaration_distance;
        double penality_reward = 0;
        if (distance_ <= critical_distance)
                penality_reward = -20;
        return distance_reward + comfort_reward + penality_reward;
}