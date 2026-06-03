#include <pybind11/pybind11.h>
#include "simulator.hpp"

namespace py = pybind11;

PYBIND11_MODULE(simulator_cpp, m) {

    py::class_<Simulator>(m, "Simulator")
        .def(py::init<>())
        .def("reset", &Simulator::reset)
        .def("step", &Simulator::step)
        .def("get_ego_velocity", &Simulator::get_ego_velocity)
        .def("get_distance", &Simulator::get_distance)
        .def("get_relative_velocity", &Simulator::get_relative_velocity)
        .def("get_time", &Simulator::get_time)
        .def("is_terminated", &Simulator::is_terminated)
        .def("is_truncated", &Simulator::is_truncated)
        .def("calculate_reward", &Simulator::calculate_reward);

}