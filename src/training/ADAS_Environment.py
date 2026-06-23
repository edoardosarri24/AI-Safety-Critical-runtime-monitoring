# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "gymnasium",
#     "numpy",
#     "pygame"
# ]
# ///

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import simulator_cpp
import pygame

class ADAS_Environment(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 10}

    def __init__(self, render_mode=None):
        super(ADAS_Environment, self).__init__()
        self.sim = simulator_cpp.Simulator()
        self.render_mode = render_mode
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
        self.window = None
        self.clock = None
        self.window_width = 800
        self.window_height = 300

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
        if self.render_mode is None:
            return

        if self.window is None:
            pygame.init()
            pygame.display.init()
            pygame.font.init()
            self.window = pygame.display.set_mode((self.window_width, self.window_height))
            pygame.display.set_caption("ADAS Safety-Critical Simulation")
            self.clock = pygame.time.Clock()

        # Canvas to draw on
        canvas = pygame.Surface((self.window_width, self.window_height))
        # Draw background (modern light slate gray/blue)
        canvas.fill((240, 244, 248))

        # Get simulation states
        ego_vel = self.sim.get_ego_velocity()
        distance = self.sim.get_distance()
        rel_vel = self.sim.get_relative_velocity()
        leader_vel = ego_vel + rel_vel
        sim_time = self.sim.get_time()

        # Calculate critical distance (dt=0.1, MIN_ACCELLERATION=-8.0)
        dt = 0.1
        min_accel = -8.0
        critical_distance = max(0.0, ego_vel * dt + (
            (ego_vel**2 - leader_vel**2) / (2 * abs(min_accel))
        ))

        # Check if RTA is active (distance <= critical_distance)
        rta_active = distance <= critical_distance

        # Draw road
        road_y = 170
        road_height = 80
        pygame.draw.rect(canvas, (44, 62, 80), (0, road_y, self.window_width, road_height)) # Road asphalt
        
        # Draw lane markings (dashed yellow)
        stripe_width = 30
        stripe_gap = 20
        stripe_y = road_y + road_height // 2 - 2
        for x in range(0, self.window_width, stripe_width + stripe_gap):
            pygame.draw.rect(canvas, (241, 196, 15), (x, stripe_y, stripe_width, 4))
        
        # Road borders
        pygame.draw.rect(canvas, (236, 240, 241), (0, road_y - 4, self.window_width, 4))
        pygame.draw.rect(canvas, (236, 240, 241), (0, road_y + road_height, self.window_width, 4))

        # Scale for rendering: 10 pixels per meter
        scale = 10.0
        ego_x = 100
        car_y = road_y + 15
        car_width = 50
        car_height = 30

        # Ego vehicle (Vibrant Blue)
        ego_rect = pygame.Rect(ego_x, car_y, car_width, car_height)
        pygame.draw.rect(canvas, (52, 152, 219), ego_rect, border_radius=5)
        # Draw wheels for Ego
        pygame.draw.circle(canvas, (30, 30, 30), (ego_x + 12, car_y + car_height), 6)
        pygame.draw.circle(canvas, (30, 30, 30), (ego_x + 38, car_y + car_height), 6)
        # Text on Ego
        font_car = pygame.font.SysFont("Arial", 11, bold=True)
        ego_lbl = font_car.render("EGO", True, (255, 255, 255))
        canvas.blit(ego_lbl, (ego_x + 12, car_y + 8))

        # Leader vehicle (Vibrant Orange)
        leader_x = ego_x + car_width + int(distance * scale)
        leader_x_draw = min(leader_x, self.window_width - car_width - 15)
        
        leader_rect = pygame.Rect(leader_x_draw, car_y, car_width, car_height)
        pygame.draw.rect(canvas, (230, 126, 34), leader_rect, border_radius=5)
        # Draw wheels for Leader
        pygame.draw.circle(canvas, (30, 30, 30), (leader_x_draw + 12, car_y + car_height), 6)
        pygame.draw.circle(canvas, (30, 30, 30), (leader_x_draw + 38, car_y + car_height), 6)
        # Text on Leader
        leader_lbl = font_car.render("LEAD", True, (255, 255, 255))
        canvas.blit(leader_lbl, (leader_x_draw + 10, car_y + 8))

        # Draw connecting line for actual distance
        line_start = ego_x + car_width
        line_end = leader_x_draw
        if line_end > line_start:
            color = (231, 76, 60) if rta_active else (46, 204, 113) # Red if RTA active, Green otherwise
            pygame.draw.line(canvas, color, (line_start, car_y + car_height // 2), (line_end, car_y + car_height // 2), 3)
            # Distance text in middle of line
            font_dist = pygame.font.SysFont("Arial", 13, bold=True)
            dist_text = font_dist.render(f"{distance:.1f} m", True, color)
            canvas.blit(dist_text, (line_start + (line_end - line_start) // 2 - 15, car_y - 15))

        # Draw Safety Margin Zone (Critical Distance)
        crit_width = int(critical_distance * scale)
        if crit_width > 0:
            crit_surf = pygame.Surface((crit_width, car_height + 10), pygame.SRCALPHA)
            crit_surf.fill((231, 76, 60, 60)) # Transparent Red
            canvas.blit(crit_surf, (ego_x + car_width, car_y - 5))
            
            # Draw critical boundary line
            pygame.draw.line(canvas, (231, 76, 60), (ego_x + car_width + crit_width, car_y - 10), (ego_x + car_width + crit_width, car_y + car_height + 10), 2)
            font_crit = pygame.font.SysFont("Arial", 11, italic=True)
            crit_lbl = font_crit.render(f"Safety Limit ({critical_distance:.1f}m)", True, (192, 57, 43))
            canvas.blit(crit_lbl, (ego_x + car_width + crit_width - 40, car_y - 25))

        # Draw Dashboard overlay
        pygame.draw.rect(canvas, (236, 240, 241), (0, 0, self.window_width, 100))
        pygame.draw.line(canvas, (189, 195, 199), (0, 100), (self.window_width, 100), 2)

        font_normal = pygame.font.SysFont("Arial", 13)
        font_status = pygame.font.SysFont("Arial", 16, bold=True)

        # Labels - Column 1
        canvas.blit(font_normal.render(f"Simulation Time: {sim_time:.2f} s", True, (44, 62, 80)), (20, 15))
        canvas.blit(font_normal.render(f"Ego Speed: {ego_vel * 3.6:.1f} km/h ({ego_vel:.2f} m/s)", True, (44, 62, 80)), (20, 40))
        canvas.blit(font_normal.render(f"Leader Speed: {leader_vel * 3.6:.1f} km/h ({leader_vel:.2f} m/s)", True, (44, 62, 80)), (20, 65))

        # Labels - Column 2
        canvas.blit(font_normal.render(f"Actual Distance: {distance:.2f} m", True, (44, 62, 80)), (300, 15))
        canvas.blit(font_normal.render(f"Critical Distance: {critical_distance:.2f} m", True, (44, 62, 80)), (300, 40))
        canvas.blit(font_normal.render(f"Relative Velocity: {rel_vel:.2f} m/s", True, (44, 62, 80)), (300, 65))

        # Labels - Column 3 (RTA Status)
        rta_text = "RTA OVERRIDE ACTIVE" if rta_active else "SAFETY MONITOR SECURE"
        rta_color = (231, 76, 60) if rta_active else (46, 204, 113)
        pygame.draw.rect(canvas, (255, 255, 255), (560, 15, 220, 70), border_radius=5)
        pygame.draw.rect(canvas, rta_color, (560, 15, 220, 70), width=2, border_radius=5)
        
        status_lbl = font_status.render(rta_text, True, rta_color)
        status_rect = status_lbl.get_rect(center=(670, 50))
        canvas.blit(status_lbl, status_rect)

        # Blit canvas to window
        self.window.blit(canvas, (0, 0))
        pygame.event.pump()
        pygame.display.update()

        # Tick at matching framerate (10 FPS for dt=0.1)
        self.clock.tick(10)

    def close(self):
        if self.window is not None:
            import pygame
            pygame.display.quit()
            pygame.quit()
            self.window = None
            self.clock = None