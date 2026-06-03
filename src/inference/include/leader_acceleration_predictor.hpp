#include <onnxruntime/onnxruntime_cxx_api.h>
#include <algorithm>

class Leader_acceleration_predictor {
    private:
        Ort::Env env_;
        Ort::Session session_;
        std::vector<const char*> input_names_;
        std::vector<const char*> output_names_;

    public:
        Leader_acceleration_predictor();
        float predict(float ego_velocity, float distance, float relative_velocity);

};
