#include <onnxruntime/onnxruntime_cxx_api.h>
#include <algorithm>
#include "leader_acceleration_predictor.hpp"
#include "global_parameters.hpp"

Leader_acceleration_predictor::Leader_acceleration_predictor() noexcept :
        env_(ORT_LOGGING_LEVEL_WARNING, "ADAS_Inference"),
        session_(env_, data::MODEL_PATH.data(), Ort::SessionOptions{nullptr}) {
    input_names_ = {"input"};
    output_names_ = {"acceleration"};
}

float Leader_acceleration_predictor::predict(float ego_velocity, float distance, float relative_velocity) {
    // Input
    std::vector<float> input{ego_velocity, distance, relative_velocity};
    std::vector<int64_t> input_shape = {1, 3};
    Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
    Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
        memory_info,
        input.data(),
        input.size(),
        input_shape.data(),
        input_shape.size()
    );

    // Inference
    auto output_tensors = session_.Run(
        Ort::RunOptions{nullptr},
        input_names_.data(),
        &input_tensor,
        1,
        output_names_.data(),
        1
    );

    // Output
    float raw_action = output_tensors[0].GetTensorMutableData<float>()[0];
    raw_action = std::clamp(raw_action, -1.0f, 1.0f);
    float acceleration = -2.5f + (raw_action * 5.5f);

    // Return
    return acceleration;
}

