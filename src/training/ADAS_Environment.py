# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "gymnasium",
#     "numpy"
# ]
# ///

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import simulator_cpp

class ADAS_Environment(gym.Env):

    def __init__(self):
        super(ADAS_Environment, self).__init__()
        self.sim = simulator_cpp.Simulator()
        self.action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(1,),
            dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, -50.0], dtype=np.float32),
            high=np.array([100.0, 200.0, 50.0], dtype=np.float32),
            dtype=np.float32
        )

    def _get_state(self):
        """Helper to construct the state array from C++ getters"""
        return np.array([
            self.sim.get_ego_velocity(),
            self.sim.get_distance(),
            self.sim.get_relative_velocity()
        ], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.sim.reset()
        state = self._get_state()
        info = {}
        return state, info

    def step(self, action):
        # Map normalized action from [-1.0,1.0] to [-8.0,3.0]
        acceleration = float(-2.5 + (action[0] * 5.5))
        self.sim.step(acceleration)
        reward = self.sim.calculate_reward(acceleration)
        state = self._get_state()
        terminated = self.sim.is_terminated()
        truncated = self.sim.is_truncated()
        info = {}
        return state, float(reward), terminated, truncated, info

    def render(self):
        """
        Optional: render the environment if required by the C++ backend.
        """
        pass