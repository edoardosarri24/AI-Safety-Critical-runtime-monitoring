# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "torch"
# ]
# ///

import torch.nn as nn
import torch
import os

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

def save_model(model):
    model.policy.eval()
    actor_model = ActorOnly(model.policy).cpu()
    actor_model.eval()
    dummy_input = torch.randn(1, 3)
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