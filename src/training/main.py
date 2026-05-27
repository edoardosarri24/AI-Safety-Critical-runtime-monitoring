# /// script
# requires-python = ">=3.9"
# dependencies = [
#       "stable_baselines3",
#       "torch"
# ]
# ///

import os
import torch.onnx
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from ADAS_Environment import ADAS_Environment

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
model.learn(total_timesteps=5000)




# Definisci la classe prima di usarla
class ActorOnly(nn.Module):
    def __init__(self, policy):
        super().__init__()
        self.features_extractor = policy.features_extractor
        self.mlp_extractor = policy.mlp_extractor
        self.action_net = policy.action_net

    def forward(self, obs):
        features = self.features_extractor(obs)
        latent_pi = self.mlp_extractor.forward_actor(features)
        return self.action_net(latent_pi)

# 1. Preparazione modello
model.policy.eval()
actor_model = ActorOnly(model.policy).cpu()
actor_model.eval() # Added to prevent the ONNX training mode warning
dummy_input = torch.randn(1, 3)

# 2. Esportazione pulita
# dynamic_shapes deve essere una tupla che contiene la definizione per ogni input.
# Per un singolo tensore, usiamo ( {0: torch.export.Dim("batch_size")}, )
os.makedirs("data", exist_ok=True)
torch.onnx.export(
    actor_model,
    (dummy_input,),
    "data/adas_model.onnx",
    input_names=['input'],
    output_names=['acceleration'],
    dynamic_shapes=(
        {0: torch.export.Dim("batch_size")},
    )
)
print("Modello esportato correttamente!")