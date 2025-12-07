
import pygame
import sys
import math
from components.grid_environment_3d import Grid3DEnvironment
from pathfinding_algorithms_3d import Pathfinding3DAlgorithms
from components.vehicle_3d import Vehicle3D
from components.ui_components import ButtonManager
from components.map_loader import OSMMapLoader

class Pathfinding3DVisualizer:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)
    DARK_GRAY = (50, 50, 50)
    LIGHT_BLUE = (173, 216, 230)
    BG_TOP = (20, 30, 50)  
    BG_BOTTOM = (60, 80, 120)  
    
    def __init__(self, rows=35, cols=35, height=5):
        pygame.init()       
        self.rows = rows
        self.cols = cols
        self.height_levels = height
        
        # Window dimensions
        self.width = 1600
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("3D Pathfinding - Vehicle Navigation with OSM")
        
        # Initialize 3D grid and pathfinder
        self.grid = Grid3DEnvironment(rows, cols, height)
        self.pathfinder = Pathfinding3DAlgorithms(self.grid)
        self.vehicle = Vehicle3D()
        
        # Isometric view settings
        self.tile_width = 15
        self.tile_height = 15
        self.offset_x = 800
        self.offset_y = 450
        self.current_level = 0 
        
        # 3D Camera settings
        self.camera_yaw = 0.0  
        self.camera_pitch = 30.0  
        self.camera_distance = 1.0  
        self.rotation_angle = 0  
        
        # Panning/dragging state
        self.is_dragging = False
        self.drag_start_pos = None
        self.drag_button = None  
        
        # Camera movement speed
        self.move_speed = 10
        
        # Building generation toggle
        self._use_recursive_buildings = False
        self.rotate_speed = 2.0
        
        # State
        self.mode = "start"  
        self.obstacle_type = "building" 
        self.algorithm = "a_star"
        self.path = []
        self.explored_nodes = []
        self.metrics = {}
        self.comparison_metrics = {}  
        self.visualizing = False
        self.step_by_step = False
        self.visualization_step = 0
        
        # Step-by-step visualization state
        self.animating_search = False
        self.animation_index = 0
        self.animation_explored = []
        self.animation_final_path = []
        self.animation_speed = 50  
        self.last_animation_time = 0
        
        # OSM Map loaded state
        self.osm_loaded = False
        self.osm_background = None  
        self.selected_start_location = 'Home'
        self.selected_end_location = 'Dubai Mall'
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 32)

        self.clock = pygame.time.Clock()
        
        location_names = OSMMapLoader.get_location_names()
        self.button_manager = ButtonManager(self.width, self.height, location_names)
        self.generate_city_environment()
    
    def generate_city_environment(self):
        self.grid.reset()
        self.grid.generate_buildings()
        self.grid.set_start(0, 2, 2)
        self.grid.set_goal(0, self.rows - 3, self.cols - 3)
        self.vehicle.position = [0, 2, 2]
    
    def load_osm_map(self):
        self.osm_background = OSMMapLoader.initialize_map(self.grid, self.rows, self.cols)
        self.vehicle.position = [0, 2, 2]
        self.osm_loaded = True
    
    def load_locations_map(self):
        start_loc = self.button_manager.start_location_dropdown.get_selected_location()
        dest_loc = self.button_manager.dest_location_dropdown.get_selected_location()
        
        self.metrics = {}
        self.animation_explored = []
        self.animation_final_path = []
        
        osm_map, start_loc, dest_loc, success = OSMMapLoader.initialize_locations_map(
            self.grid, self.vehicle, start_loc, dest_loc, self.rows
        )
        
        if success:
            self.osm_background = osm_map
            self.osm_loaded = True
            self.selected_start_location = start_loc
            self.selected_end_location = dest_loc
        else:
            self.load_osm_map()
    
    def cart_to_iso(self, x, y, z):
        # Center coordinates
        cx, cy, cz = self.cols / 2, self.rows / 2, self.height_levels / 2
        x_rel = x - cx
        y_rel = y - cy
        z_rel = z - cz
          
        yaw_rad = math.radians(self.camera_yaw)
        cos_yaw = math.cos(yaw_rad)
        sin_yaw = math.sin(yaw_rad)
        
        x_yaw = x_rel * cos_yaw - y_rel * sin_yaw
        y_yaw = x_rel * sin_yaw + y_rel * cos_yaw
        z_yaw = z_rel
              
        pitch_rad = math.radians(self.camera_pitch)
        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)
        
        x_final = x_yaw
        y_final = y_yaw * cos_pitch - z_yaw * sin_pitch
        z_final = y_yaw * sin_pitch + z_yaw * cos_pitch
        
        scale = self.tile_width / 2 * self.camera_distance
        iso_x = (x_final - y_final) * scale + self.offset_x
        iso_y = (x_final + y_final) * self.tile_height / 2 * self.camera_distance - z_final * self.tile_height * 2 * self.camera_distance + self.offset_y
        
        return iso_x, iso_y
    
    def iso_to_cart(self, iso_x, iso_y):
        iso_x -= self.offset_x
        iso_y -= self.offset_y
        scale = self.tile_width / 2 * self.camera_distance
        
        x_plus_y = iso_y / (self.tile_height / 2 * self.camera_distance)
        x_minus_y = iso_x / scale
        
        x_rotated = (x_plus_y + x_minus_y) / 2
        y_rotated = (x_plus_y - x_minus_y) / 2
        
        yaw_rad = -math.radians(self.camera_yaw)
        cos_yaw = math.cos(yaw_rad)
        sin_yaw = math.sin(yaw_rad)
        
        cx, cy = self.cols / 2, self.rows / 2
        
        x_rel = x_rotated - cx
        y_rel = y_rotated - cy
        
        x = x_rel * cos_yaw - y_rel * sin_yaw + cx
        y = x_rel * sin_yaw + y_rel * cos_yaw + cy
        
        return int(round(y)), int(round(x)), 0
    
    def get_cell_from_mouse(self, pos):
        mouse_x, mouse_y = pos
        min_dist = float('inf')
        closest_cell = None
        
        for row in range(self.rows):
            for col in range(self.cols):
                iso_x, iso_y = self.cart_to_iso(col + 0.5, row + 0.5, 0)
                dist = math.sqrt((mouse_x - iso_x)**2 + (mouse_y - iso_y)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest_cell = (0, row, col)
        
        if min_dist < self.tile_width:
            return closest_cell
        return None
    
    def draw_ground_plane(self):
        corners = []
        corner_coords = [(0, 0), (self.cols, 0), (self.cols, self.rows), (0, self.rows)]
        for col, row in corner_coords:
            x, y = self.cart_to_iso(col, row, 0)
            corners.append((x, y))
        if self.osm_background:
            min_x = min(c[0] for c in corners)
            max_x = max(c[0] for c in corners)
            min_y = min(c[1] for c in corners)
            max_y = max(c[1] for c in corners)
            
            width = int(max_x - min_x)
            height = int(max_y - min_y)
            scaled_map = pygame.transform.smoothscale(self.osm_background, (width, height))
            
            plane_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            plane_surface.blit(scaled_map, (0, 0))

            mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            mask_corners = [(c[0] - min_x, c[1] - min_y) for c in corners]
            pygame.draw.polygon(mask_surface, (255, 255, 255, 255), mask_corners)

            plane_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            self.screen.blit(plane_surface, (min_x, min_y))
        else:
            pygame.draw.polygon(self.screen, (255, 255, 255), corners)
        
        
        if not self.osm_loaded:
            for col in range(self.cols + 1):
                p1 = self.cart_to_iso(col, 0, 0)
                p2 = self.cart_to_iso(col, self.rows, 0)
                pygame.draw.line(self.screen, (100, 100, 100), p1, p2, 1)
            
            for row in range(self.rows + 1):
                p1 = self.cart_to_iso(0, row, 0)
                p2 = self.cart_to_iso(self.cols, row, 0)
                pygame.draw.line(self.screen, (100, 100, 100), p1, p2, 1)
    
    def draw_3d_grid(self):
        self.draw_ground_plane()

        if self.animation_explored:
            s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
            for z, row, col in self.animation_explored:
                corners = [
                    self.cart_to_iso(col, row, z),
                    self.cart_to_iso(col + 1, row, z),
                    self.cart_to_iso(col + 1, row + 1, z),
                    self.cart_to_iso(col, row + 1, z)
                ]
                pygame.draw.polygon(s, (*self.CYAN, 200), corners)
            self.screen.blit(s, (0, 0))

        
        if not self.osm_loaded:
            for col in range(self.cols + 1):
                p1 = self.cart_to_iso(col, 0, 0)
                p2 = self.cart_to_iso(col, self.rows, 0)
                pygame.draw.line(self.screen, (100, 100, 100), p1, p2, 1)
            
            for row in range(self.rows + 1):
                p1 = self.cart_to_iso(0, row, 0)
                p2 = self.cart_to_iso(self.cols, row, 0)
                pygame.draw.line(self.screen, (100, 100, 100), p1, p2, 1)
        
        path_points = []
        
        for row in range(self.rows):
            for col in range(self.cols):
                cell_type = self.grid.grid[0, row, col]
                iso_x, iso_y = self.cart_to_iso(col + 0.5, row + 0.5, 0)
                
                if cell_type == Grid3DEnvironment.START:
                    pygame.draw.circle(self.screen, self.GREEN, (int(iso_x), int(iso_y)), 6)
                    pygame.draw.circle(self.screen, (0, 0, 0), (int(iso_x), int(iso_y)), 6, 2)
                elif cell_type == Grid3DEnvironment.GOAL:
                    pygame.draw.circle(self.screen, self.RED, (int(iso_x), int(iso_y)), 6)
                    pygame.draw.circle(self.screen, (0, 0, 0), (int(iso_x), int(iso_y)), 6, 2)
                elif cell_type == Grid3DEnvironment.CAR:
                    Vehicle3D.draw_car_obstacle(self.screen, iso_x, iso_y, self.tile_width, self.tile_height)
                elif cell_type == Grid3DEnvironment.PATH:
                    path_points.append((int(iso_x), int(iso_y)))
        
        if len(path_points) > 1:
            for i in range(len(path_points) - 1):
                pygame.draw.line(self.screen, self.YELLOW, path_points[i], path_points[i + 1], 8)
        
        for z in range(1, self.height_levels):  
            for row in range(self.rows - 1, -1, -1):
                for col in range(self.cols):
                    self.draw_cell(z, row, col)
    
    def draw_cell(self, z, row, col):
        cell_type = self.grid.grid[z, row, col]
        
        if z > 0 and cell_type == Grid3DEnvironment.EMPTY:
            if z > self.current_level + 2:
                return
        
        iso_x, iso_y = self.cart_to_iso(col + 0.5, row + 0.5, z)
        
        if cell_type == Grid3DEnvironment.OBSTACLE:
            color = (80, 80, 80)
            self.draw_cube(iso_x, iso_y, color, z)
    
    def draw_marker(self, iso_x, iso_y, color, alpha=255):
        half_w = self.tile_width / 2
        half_h = self.tile_height / 2
        
        points = [
            (iso_x, iso_y - half_h),
            (iso_x + half_w, iso_y),
            (iso_x, iso_y + half_h),
            (iso_x - half_w, iso_y)
        ]
        
        if alpha < 255:
            bbox_w = int(self.tile_width) + 2
            bbox_h = int(self.tile_height) + 2
            s = pygame.Surface((bbox_w, bbox_h), pygame.SRCALPHA)
            local_points = [(p[0] - iso_x + bbox_w//2, p[1] - iso_y + bbox_h//2) for p in points]
            pygame.draw.polygon(s, (*color, alpha), local_points)
            self.screen.blit(s, (iso_x - bbox_w//2, iso_y - bbox_h//2))
        else:
            pygame.draw.polygon(self.screen, color, points)
    
    def draw_tile(self, iso_x, iso_y, color, z, alpha=255):
        points = [
            (iso_x, iso_y),
            (iso_x + self.tile_width / 2, iso_y + self.tile_height / 2),
            (iso_x, iso_y + self.tile_height),
            (iso_x - self.tile_width / 2, iso_y + self.tile_height / 2)
        ]
        
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, self.DARK_GRAY, points, 1)
    
    def draw_cube(self, iso_x, iso_y, color, z):
        h = self.tile_height * 2  

        top_points = [
            (iso_x, iso_y - h),
            (iso_x + self.tile_width / 2, iso_y - h + self.tile_height / 2),
            (iso_x, iso_y - h + self.tile_height),
            (iso_x - self.tile_width / 2, iso_y - h + self.tile_height / 2)
        ]

        left_points = [
            (iso_x - self.tile_width / 2, iso_y + self.tile_height / 2),
            (iso_x, iso_y + self.tile_height),
            (iso_x, iso_y - h + self.tile_height),
            (iso_x - self.tile_width / 2, iso_y - h + self.tile_height / 2)
        ]

        right_points = [
            (iso_x, iso_y + self.tile_height),
            (iso_x + self.tile_width / 2, iso_y + self.tile_height / 2),
            (iso_x + self.tile_width / 2, iso_y - h + self.tile_height / 2),
            (iso_x, iso_y - h + self.tile_height)
        ]
        
        darker = tuple(max(0, c - 40) for c in color)
        darkest = tuple(max(0, c - 60) for c in color)
        
        pygame.draw.polygon(self.screen, darkest, left_points)
        pygame.draw.polygon(self.screen, darker, right_points)
        pygame.draw.polygon(self.screen, color, top_points)
        
        pygame.draw.polygon(self.screen, self.BLACK, top_points, 1)
        pygame.draw.polygon(self.screen, self.BLACK, left_points, 1)
        pygame.draw.polygon(self.screen, self.BLACK, right_points, 1)
    
    def draw_vehicle(self):
        if self.vehicle.position:
            z, row, col = self.vehicle.position
            iso_x, iso_y = self.cart_to_iso(col, row, z)
            self.vehicle.draw(self.screen, iso_x, iso_y - 5)
    
    def draw_comparison_table(self):
        table_x = 200
        table_y = 120
        table_width = 280
        table_height = 140
        
        # Background with border
        bg_surface = pygame.Surface((table_width, table_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (20, 25, 35, 230), bg_surface.get_rect(), border_radius=10)
        self.screen.blit(bg_surface, (table_x, table_y))
        pygame.draw.rect(self.screen, (100, 181, 246), (table_x, table_y, table_width, table_height), 2, border_radius=10)
        
        title_font = pygame.font.Font(None, 22)
        algo_name = "A* Algorithm" if self.algorithm == 'a_star' else "Dijkstra Algorithm"
        title_text = title_font.render(algo_name, True, (100, 181, 246))
        self.screen.blit(title_text, (table_x + 80, table_y + 10))
        
        
        # Metrics display
        data_y = table_y + 55
        metric_font = pygame.font.Font(None, 18)
        
        metrics_data = [
            ("Nodes Explored:", self.metrics.get('nodes_explored', 0)),
            ("Path Length:", self.metrics.get('path_length', 0)),
            ("Execution Time:", f"{self.metrics.get('execution_time', 0)*1000:.4f} ms")
        ]
        
        for i, (label, value) in enumerate(metrics_data):
            y_pos = data_y + i * 30
            
            # Label
            label_text = metric_font.render(label, True, (200, 200, 200))
            self.screen.blit(label_text, (table_x + 20, y_pos))
            
            # Value
            value_text = metric_font.render(str(value), True, (46, 204, 113))
            self.screen.blit(value_text, (table_x + 180, y_pos))
    
    def draw_route_info(self):
        if not self.osm_loaded:
            return
        
        # metrics table with 2 rows spacing (80px)
        table_x = 200
        table_y = 120 + 150 + 80  
        table_width = 200
        table_height = 110
        
        bg_surface = pygame.Surface((table_width, table_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect(), border_radius=12)
        self.screen.blit(bg_surface, (table_x, table_y))
        
        pygame.draw.rect(self.screen, (70, 130, 180), (table_x, table_y, table_width, table_height), 2, border_radius=12)
        
        # Title
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render("Route:", True, (200, 200, 200))
        self.screen.blit(title_text, (table_x + 20, table_y + 15))
        
        # From location
        label_font = pygame.font.Font(None, 18)
        from_label = label_font.render("From:", True, (200, 200, 200))
        self.screen.blit(from_label, (table_x + 20, table_y + 50))
        
        from_value = label_font.render(self.selected_start_location, True, (46, 204, 113))
        self.screen.blit(from_value, (table_x + 75, table_y + 50))
        
        # To location
        to_label = label_font.render("To:", True, (200, 200, 200))
        self.screen.blit(to_label, (table_x + 20, table_y + 75))
        
        to_value = label_font.render(self.selected_end_location, True, (231, 76, 60))
        self.screen.blit(to_value, (table_x + 75, table_y + 75))
    
    def draw_ui(self):
        if self.metrics:
            self.draw_comparison_table()
        
        self.draw_route_info()
        
        self.button_manager.draw(self.screen)

        mode_text = f"Mode: {self.mode.upper()}"
        mode_surface = self.font.render(mode_text, True, self.YELLOW)
        self.screen.blit(mode_surface, (20, 720))
        
        camera_yaw_text = f"Yaw: {self.camera_yaw:.1f}°"
        camera_surface = self.font.render(camera_yaw_text, True, self.WHITE)
        self.screen.blit(camera_surface, (20, 750))
        
        camera_pitch_text = f"Pitch: {self.camera_pitch:.1f}°"
        pitch_surface = self.font.render(camera_pitch_text, True, self.WHITE)
        self.screen.blit(pitch_surface, (20, 780))
        
        controls_text = "Left-Click+Drag: Rotate 3D | Mouse Wheel: Zoom"
        controls_surface = self.small_font.render(controls_text, True, (150, 150, 150))
        self.screen.blit(controls_surface, (20, 810))
        
        if self.osm_loaded:
            osm_text = "OSM: LOADED"
            osm_surface = self.small_font.render(osm_text, True, self.GREEN)
            self.screen.blit(osm_surface, (20, 840))

        title_text = "3D PATHFINDING"
        title_font = pygame.font.Font(None, 32)
        
        bg_width = 190
        bg_height = 30
        bg_rect = pygame.Rect((self.width - bg_width) // 2 - 510, self.height - 150, bg_width, bg_height)
        pygame.draw.rect(self.screen, (20, 25, 35), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2, border_radius=5)

        shadow_surface = title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.width // 2 - 509, self.height - 133))
        self.screen.blit(shadow_surface, shadow_rect)

        title_surface = title_font.render(title_text, True, (100, 200, 255))
        title_rect = title_surface.get_rect(center=(self.width // 2 - 510, self.height - 135))
        self.screen.blit(title_surface, title_rect)
    
    def handle_button_click(self, pos):
        return self.button_manager.handle_click(pos, self)
    
    def handle_grid_click(self, pos):
        cell = self.get_cell_from_mouse(pos)
        if cell:
            z, row, col = cell
            
            if self.mode == 'start':
                self.grid.set_start(0, row, col)  
                self.vehicle.position = [0, row, col]
                return True
            elif self.mode == 'goal':
                self.grid.set_goal(0, row, col)
                return True  
            elif self.mode == 'obstacle':
                if self.obstacle_type == 'car':
                    self.grid.add_car(0, row, col)
                else:
                    
                    building_height = min(4, self.height_levels)  
                    for level in range(building_height):
                        self.grid.add_obstacle(level, row, col)
                return True
            elif self.mode == 'erase':
                for level in range(self.height_levels):
                    self.grid.remove_obstacle(level, row, col)
                self.grid.remove_obstacle(0, row, col)
                return True
        return False
    
    def run_pathfinding(self):
        if not self.grid.start or not self.grid.goal:
            print("Please set both start and goal!")
            return
        
        # Reset vehicle to start position
        self.vehicle.position = list(self.grid.start)
        self.vehicle.path = []
        self.vehicle.path_index = 0
        
        self.grid.clear_path_visualization()
        
        print(f"\nRunning {self.algorithm.upper().replace('_', ' ')}...")
        
        if self.algorithm == 'dijkstra':
            path, metrics = self.pathfinder.dijkstra(self.grid.start, self.grid.goal)
        else:
            path, metrics = self.pathfinder.a_star(self.grid.start, self.grid.goal)
        
        self.metrics = metrics
        
        if path:
            print(f"✓ Path found! Length: {len(path)}")
            print(f"  Explored nodes: {len(metrics['explored_nodes'])}")

            self.animating_search = True
            self.animation_index = 0
            self.animation_explored = []
            self.animation_final_path = path.copy()
            self.explored_nodes = metrics['explored_nodes'].copy()
            self.last_animation_time = pygame.time.get_ticks()
        else:
            print("✗ No path found!")
    
    def run(self):
        running = True
        
        while running:
            self.clock.tick(60)         
            current_time = pygame.time.get_ticks()
            if self.animating_search and current_time - self.last_animation_time > self.animation_speed:
                self.last_animation_time = current_time

                if self.animation_index < len(self.explored_nodes):
                    self.animation_explored.append(self.explored_nodes[self.animation_index])
                    self.animation_index += 1
                else:
                    self.animating_search = False
                    self.grid.mark_path(self.animation_final_path)
                    self.vehicle.set_path(self.animation_final_path)
                    print("✓ Search animation complete, vehicle moving!")
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False             
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Check if clicking on UI first
                        if not self.handle_button_click(event.pos):
                            # If not on UI, check if on grid
                            if not self.handle_grid_click(event.pos):
                                # If not on grid either, start dragging
                                self.is_dragging = True
                                self.drag_start_pos = event.pos
                                self.drag_button = 1            
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_dragging = False
                        self.drag_start_pos = None
                        self.drag_button = None              
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_dragging and self.drag_start_pos:
                        dx = event.pos[0] - self.drag_start_pos[0]
                        dy = event.pos[1] - self.drag_start_pos[1]
                        self.camera_yaw += dx * 0.3
                        if self.camera_yaw >= 360:
                            self.camera_yaw -= 360
                        elif self.camera_yaw < 0:
                            self.camera_yaw += 360                      
                        self.camera_pitch -= dy * 0.3
                        self.camera_pitch = max(-90, min(90, self.camera_pitch))     
                        self.drag_start_pos = event.pos

                    self.button_manager.handle_event(event)
                elif event.type == pygame.MOUSEWHEEL:
                    self.camera_distance += event.y * -0.1
                    self.camera_distance = max(0.5, min(2.5, self.camera_distance))
            
            self.vehicle.update()
            
            for y in range(self.height):
                progress = y / self.height
                color = (
                    int(self.BG_TOP[0] + (self.BG_BOTTOM[0] - self.BG_TOP[0]) * progress),
                    int(self.BG_TOP[1] + (self.BG_BOTTOM[1] - self.BG_TOP[1]) * progress),
                    int(self.BG_TOP[2] + (self.BG_BOTTOM[2] - self.BG_TOP[2]) * progress)
                )
                pygame.draw.line(self.screen, color, (0, y), (self.width, y))
            self.draw_3d_grid()
            self.draw_vehicle()
            self.draw_ui()
            
            pygame.display.flip()       
        pygame.quit()
        sys.exit()
