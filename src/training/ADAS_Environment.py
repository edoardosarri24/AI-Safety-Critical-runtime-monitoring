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

class ADAS_Environment(gym.Env):
    
    def __init__(self):
        super(ADAS_Environment, self).__init__()
        # Initialize the underlying C++ simulator instance
        # self.sim = adas_simulator_cpp.Simulator()
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

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # self.sim.reset(seed)
        # state = self.sim.get_state() 
        
        # Placeholder for the state: [v_E(0), d(0), v_rel(0)]
        state = np.array([15.0, 10.0, 0.0], dtype=np.float32)

        info = {}
        return state, info

    def step(self, action):
        # Map normlized action from [-1.0,1-0] to [-8.0,3.0].
        acceleration = -2.5 + (action[0] * 5.5)
        
        # self.sim.step(acceleration)
        # state = self.sim.get_state()
        # reward = self.sim.calculate_reward()
        # terminated = self.sim.is_terminated() # Checks collision or leader lost
        # truncated = self.sim.is_truncated()   # Checks 30s timeout
        
        # Placeholders
        state = np.array([15.0, 10.0, 0.0], dtype=np.float32)
        reward = 0.1
        terminated = False
        truncated = False
        info = {}

        return state, reward, terminated, truncated, info

    def render(self):
        """
        Optional: render the environment if required by the C++ backend.
        """
        pass