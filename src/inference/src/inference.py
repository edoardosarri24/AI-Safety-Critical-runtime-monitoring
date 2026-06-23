# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "gymnasium",
#     "numpy",
#     "pygame",
#     "onnxruntime"
# ]
# ///

import os
import sys
import numpy as np
import onnxruntime as ort
import pygame

# Find project root and add src/training to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src", "training"))

from ADAS_Environment import ADAS_Environment

def main():
    onnx_path = os.path.join(PROJECT_ROOT, "data", "adas_model.onnx")
    if not os.path.exists(onnx_path):
        print(f"Error: ONNX model not found at {onnx_path}")
        print("Please train the model first by running the training script.")
        return

    # Load ONNX model
    print(f"Loading ONNX model from {onnx_path}...")
    try:
        ort_session = ort.InferenceSession(onnx_path)
    except Exception as e:
        print(f"Failed to load ONNX model: {e}")
        return

    # Initialize Gymnasium environment with 'human' rendering
    print("Initializing Gymnasium environment with GUI rendering...")
    env = ADAS_Environment(render_mode="human")
    obs, info = env.reset()
    env.render()  # Initialize pygame and render the initial state

    # Simulation control variables
    terminated = False
    truncated = False
    use_rta = True  # Toggle RTA filter
    total_ticks = 0
    rta_interventions = 0
    paused = False

    print("\n--- Controls in Simulation Window ---")
    print("  [R]     : Toggle RTA Safety Filter (Runtime Assurance)")
    print("  [Space] : Pause / Resume simulation")
    print("  [Esc]   : Quit simulation")
    print("--------------------------------------\n")

    # Physics parameter limits (matching C++ global_parameters.hpp)
    MIN_ACCELLERATION = -8.0
    dt = 0.1

    while not (terminated or truncated):
        # Handle pygame events (window close, keystrokes)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminated = True
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    print("Simulation PAUSED" if paused else "Simulation RESUMED")
                elif event.key == pygame.K_r:
                    use_rta = not use_rta
                    print(f"RTA Safety Filter: {'ENABLED' if use_rta else 'DISABLED'}")

        if paused:
            # Re-render to keep the window responsive during pause
            env.render()
            pygame.time.wait(100)
            continue

        # 1. State sensors
        ego_velocity = env.sim.get_ego_velocity()
        relative_velocity = env.sim.get_relative_velocity()
        leader_velocity = ego_velocity + relative_velocity
        actual_distance = env.sim.get_distance()

        # Calculate critical distance
        critical_distance = max(0.0, ego_velocity * dt + (
            (ego_velocity**2 - leader_velocity**2) / (2 * abs(MIN_ACCELLERATION))
        ))

        # 2. Safety Monitor decision (RTA Override check)
        rta_active = (actual_distance <= critical_distance) and use_rta

        if rta_active:
            # Override action with safe deceleration (maps to normalized action -1.0)
            acceleration = MIN_ACCELLERATION
            rta_interventions += 1
            normalized_action = np.array([(acceleration + 2.5) / 5.5], dtype=np.float32)
        else:
            # Let the AI predict action
            # Prepare state observation for ONNX: Shape [1, 3]
            input_data = obs.reshape(1, 3).astype(np.float32)
            ort_inputs = {ort_session.get_inputs()[0].name: input_data}
            ort_outs = ort_session.run(None, ort_inputs)
            normalized_action = ort_outs[0][0] # Shape (1,)

        # 3. Environment Step
        obs, reward, terminated, truncated, info = env.step(normalized_action)
        total_ticks += 1

        # 4. Render
        env.render()
        
        # Overlay custom RTA toggle information in window title
        pygame.display.set_caption(f"ADAS Safety-Critical Simulation - RTA: {'ON (R to toggle)' if use_rta else 'OFF (R to toggle)'}")

    # End simulation
    env.close()

    # Results summary
    print("\n================ Simulation Results ================")
    final_distance = env.sim.get_distance()
    if final_distance <= 0.0:
        print("Outcome            : COLLISION DETECTED!")
    elif final_distance >= 50.0: # MAX_DISTANCE
        print("Outcome            : LEADER VEHICLE LOST (Tracking failed)!")
    else:
        print("Outcome            : Simulation completed successfully.")

    print(f"Total Time         : {total_ticks * dt:.1f} s ({total_ticks} ticks)")
    if use_rta or rta_interventions > 0:
        print(f"RTA Interventions  : {rta_interventions} ticks ({rta_interventions * 100.0 / total_ticks:.1f}%)")
        print(f"AI Decisions       : {total_ticks - rta_interventions} ticks ({(total_ticks - rta_interventions) * 100.0 / total_ticks:.1f}%)")
    print(f"RTA Safety Filter  : {'ENABLED' if use_rta else 'DISABLED (at simulation end)'}")
    print(f"Final Distance     : {final_distance:.2f} m")
    print(f"Final Ego Speed    : {env.sim.get_ego_velocity() * 3.6:.1f} km/h")
    print("====================================================")

if __name__ == "__main__":
    main()
