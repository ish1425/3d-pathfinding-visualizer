
import pygame
import math
from typing import Tuple

class Vehicle3D:
    def __init__(self, position: Tuple[int, int, int] = (0, 0, 0)):
        self.position = list(position)  # [z, row, col]
        self.target_position = list(position)
        self.path = []
        self.path_index = 0
        self.moving = False
        self.speed = 0.1  # Movement speed
        self.rotation = 0  # Vehicle rotation angle
        
        # Vehicle appearance
        self.color = (0, 255, 255)  
        self.size = 8
    
    def set_path(self, path):
        if path and len(path) > 0:
            self.path = path
            self.path_index = 0
            self.position = list(path[0])
            self.target_position = list(path[0])
            self.moving = True
    
    def update(self):
        if not self.moving or not self.path:
            return
        
        # Move towards target position
        if self.path_index < len(self.path):
            target = self.path[self.path_index]
            
            # Calculate direction
            dz = target[0] - self.position[0]
            dr = target[1] - self.position[1]
            dc = target[2] - self.position[2]
            
            # Move towards target
            if abs(dz) > 0.05:
                self.position[0] += self.speed * (1 if dz > 0 else -1)
            if abs(dr) > 0.05:
                self.position[1] += self.speed * (1 if dr > 0 else -1)
            if abs(dc) > 0.05:
                self.position[2] += self.speed * (1 if dc > 0 else -1)
            
            # Update rotation based on movement direction
            if abs(dc) > 0.01 or abs(dr) > 0.01:
                self.rotation = math.atan2(dc, dr)
            
            # Checking if reached target
            dist = abs(dz) + abs(dr) + abs(dc)
            if dist < 0.2:
                self.path_index += 1
                if self.path_index >= len(self.path):
                    self.moving = False
                    self.path_index = len(self.path) - 1
    
    def draw(self, surface, iso_x, iso_y):
        # vehicle body
        points = self._get_vehicle_points(iso_x, iso_y)
        pygame.draw.polygon(surface, self.color, points)
        
        # direction indicator
        front_x = iso_x + math.sin(self.rotation) * self.size
        front_y = iso_y - math.cos(self.rotation) * self.size
        pygame.draw.line(surface, (255, 255, 0), (iso_x, iso_y), (front_x, front_y), 2)
        
        # wheels
        pygame.draw.circle(surface, (50, 50, 50), (int(iso_x - 3), int(iso_y + 3)), 2)
        pygame.draw.circle(surface, (50, 50, 50), (int(iso_x + 3), int(iso_y + 3)), 2)
    
    def _get_vehicle_points(self, center_x, center_y):
        half_width = self.size * 0.6
        half_height = self.size      
        # Points relative to center, then rotated
        points = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]      
        # Rotate and translate points
        rotated_points = []
        for px, py in points:
            # Rotate
            rot_x = px * math.cos(self.rotation) - py * math.sin(self.rotation)
            rot_y = px * math.sin(self.rotation) + py * math.cos(self.rotation)
            # Translate
            rotated_points.append((center_x + rot_x, center_y + rot_y))
        
        return rotated_points
    
    def stop(self):
        self.moving = False
    
    def reset(self):
        self.path = []
        self.path_index = 0
        self.moving = False
    
    @staticmethod
    def draw_car_obstacle(surface, iso_x, iso_y, tile_width, tile_height):
        car_width = tile_width * 0.7
        car_length = tile_height * 0.8
        car_height = 8  
        taxi_yellow = (255, 215, 0)
        black = (0, 0, 0)
        
        body_points = [
            (iso_x - car_width/2, iso_y - car_length/2),
            (iso_x + car_width/2, iso_y - car_length/2),
            (iso_x + car_width/2, iso_y + car_length/2),
            (iso_x - car_width/2, iso_y + car_length/2)
        ]

        shadow_points = [(x, y + 2) for x, y in body_points]
        pygame.draw.polygon(surface, (0, 0, 0, 100), shadow_points)

        pygame.draw.polygon(surface, taxi_yellow, body_points)
        pygame.draw.polygon(surface, black, body_points, 1)
        
        windshield_points = [
            (iso_x - car_width/3, iso_y - car_length/2 + 2),
            (iso_x + car_width/3, iso_y - car_length/2 + 2),
            (iso_x + car_width/3, iso_y - car_length/4),
            (iso_x - car_width/3, iso_y - car_length/4)
        ]
        pygame.draw.polygon(surface, (100, 120, 140), windshield_points)
        pygame.draw.polygon(surface, black, windshield_points, 1)
  
        rear_window_points = [
            (iso_x - car_width/3, iso_y + car_length/4),
            (iso_x + car_width/3, iso_y + car_length/4),
            (iso_x + car_width/3, iso_y + car_length/2 - 2),
            (iso_x - car_width/3, iso_y + car_length/2 - 2)
        ]
        pygame.draw.polygon(surface, (100, 120, 140), rear_window_points)
        pygame.draw.polygon(surface, black, rear_window_points, 1)
 
        # Left window
        pygame.draw.rect(surface, (100, 120, 140), 
                        (iso_x - car_width/2 + 1, iso_y - car_length/5, car_width/8, car_length/2.5))
        # Right window  
        pygame.draw.rect(surface, (100, 120, 140), 
                        (iso_x + car_width/2 - car_width/8 - 1, iso_y - car_length/5, car_width/8, car_length/2.5))
        
        # Roof light 
        roof_light_w = 4
        roof_light_h = 2
        pygame.draw.rect(surface, (255, 50, 50), 
                        (iso_x - roof_light_w/2, iso_y - car_height, roof_light_w, roof_light_h))
        
        # Wheels 
        wheel_radius = 2
        wheel_offset_x = car_width/2.5
        wheel_offset_y = car_length/3
        
        # Front-left wheel
        pygame.draw.circle(surface, (30, 30, 30), 
                         (int(iso_x - wheel_offset_x), int(iso_y - wheel_offset_y)), wheel_radius)
        pygame.draw.circle(surface, (100, 100, 100), 
                         (int(iso_x - wheel_offset_x), int(iso_y - wheel_offset_y)), wheel_radius - 1)
        
        # Front-right wheel
        pygame.draw.circle(surface, (30, 30, 30), 
                         (int(iso_x + wheel_offset_x), int(iso_y - wheel_offset_y)), wheel_radius)
        pygame.draw.circle(surface, (100, 100, 100), 
                         (int(iso_x + wheel_offset_x), int(iso_y - wheel_offset_y)), wheel_radius - 1)
        
        # Back-left wheel
        pygame.draw.circle(surface, (30, 30, 30), 
                         (int(iso_x - wheel_offset_x), int(iso_y + wheel_offset_y)), wheel_radius)
        pygame.draw.circle(surface, (100, 100, 100), 
                         (int(iso_x - wheel_offset_x), int(iso_y + wheel_offset_y)), wheel_radius - 1)
        
        # Back-right wheel
        pygame.draw.circle(surface, (30, 30, 30), 
                         (int(iso_x + wheel_offset_x), int(iso_y + wheel_offset_y)), wheel_radius)
        pygame.draw.circle(surface, (100, 100, 100), 
                         (int(iso_x + wheel_offset_x), int(iso_y + wheel_offset_y)), wheel_radius - 1)
        
        pygame.draw.circle(surface, (255, 255, 200), 
                         (int(iso_x - car_width/4), int(iso_y - car_length/2 + 1)), 1)
        pygame.draw.circle(surface, (255, 255, 200), 
                         (int(iso_x + car_width/4), int(iso_y - car_length/2 + 1)), 1)

        pygame.draw.circle(surface, (255, 0, 0), 
                         (int(iso_x - car_width/4), int(iso_y + car_length/2 - 1)), 1)
        pygame.draw.circle(surface, (255, 0, 0), 
                         (int(iso_x + car_width/4), int(iso_y + car_length/2 - 1)), 1)
