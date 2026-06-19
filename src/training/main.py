# /// script
# requires-python = ">=3.9"
# dependencies = [
#       "stable_baselines3",
#       "torch",
#       "pybind11"
# ]
# ///

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from ADAS_Environment import ADAS_Environment
from save_model import save_model

# Environment
env = ADAS_Environment()
check_env(env, warn=True)

# Model
model = PPO(
    "MlpPolicy",
    env,
    gamma=0.99,
    batch_size=64,
    n_steps=1024,
    clip_range=0.2,
    verbose=1,
    policy_kwargs=dict(
        net_arch=dict(
            pi=[16, 32, 32, 16], # Policy (actor)
            vf=[16, 32, 32, 16])) # Value (critic)
)

# Compute
model.learn(total_timesteps=500000)
save_model(model)