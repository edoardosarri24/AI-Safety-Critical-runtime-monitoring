#ifndef LEADER_ACCELERATION_PREDICTOR_HPP
#define LEADER_ACCELERATION_PREDICTOR_HPP

#include <onnxruntime/onnxruntime_cxx_api.h>
#include <algorithm>

class Leader_acceleration_predictor {
    private:
        Ort::Env env_;
        Ort::Session session_;
        std::vector<const char*> input_names_;
        std::vector<const char*> output_names_;

    public:
        Leader_acceleration_predictor() noexcept = default;
        float predict(float ego_velocity, float distance, float relative_velocity);

};

#endif // LEADER_ACCELERATION_PREDICTOR_HPP