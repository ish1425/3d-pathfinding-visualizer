
import pygame
import random

#Button style
class Button:
    def __init__(self, x, y, width, height, text, color=(70, 130, 180), hover_color=(100, 160, 210)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 18)
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        
        for i in range(4, 0, -1):
            glow_rect = self.rect.inflate(i * 2, i * 2)
            glow_alpha = 15 * (5 - i)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_color = (*color, glow_alpha)
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=20)
            surface.blit(glow_surface, (glow_rect.x, glow_rect.y))

        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_color = (20, 25, 35, 180)  
        pygame.draw.rect(bg_surface, bg_color, bg_surface.get_rect(), border_radius=18)
        surface.blit(bg_surface, (self.rect.x, self.rect.y))
        
        fill_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        fill_color = (*color, 100)  # More transparent
        pygame.draw.rect(fill_surface, fill_color, fill_surface.get_rect(), border_radius=18)
        surface.blit(fill_surface, (self.rect.x, self.rect.y))

        border_color = tuple(min(255, c + 60) for c in color)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=18)

        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Dropdown:
    def __init__(self, x, y, width, height, options, default=0, color=(70, 130, 180)):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected = default
        self.color = color
        self.is_open = False
        self.font = pygame.font.Font(None, 18)
        self.option_rects = []
        
    def draw(self, surface):
        for i in range(4, 0, -1):
            glow_rect = self.rect.inflate(i * 2, i * 2)
            glow_alpha = 15 * (5 - i)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_color = (*self.color, glow_alpha)
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=20)
            surface.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (20, 25, 35, 180), bg_surface.get_rect(), border_radius=18)
        surface.blit(bg_surface, (self.rect.x, self.rect.y))
        
        fill_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (*self.color, 100), fill_surface.get_rect(), border_radius=18)
        surface.blit(fill_surface, (self.rect.x, self.rect.y))
        
        border_color = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=18)
        
        text = self.options[self.selected]
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        arrow = "▼" if not self.is_open else "▲"
        arrow_surface = self.font.render(arrow, True, (255, 255, 255))
        surface.blit(arrow_surface, (self.rect.right - 20, self.rect.y + 8))
        
        if self.is_open:
            self.option_rects = []
            for i, option in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height * (i + 1), 
                                      self.rect.width, self.rect.height)
                self.option_rects.append((opt_rect, i))
                
                # Highlighting hovered option
                opt_color = (100, 160, 210) if opt_rect.collidepoint(pygame.mouse.get_pos()) else self.color
                
                #background
                bg_surface = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(bg_surface, (20, 25, 35, 180), bg_surface.get_rect(), border_radius=18)
                surface.blit(bg_surface, (opt_rect.x, opt_rect.y))
                
                # Colored fill
                fill_surface = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(fill_surface, (*opt_color, 100), fill_surface.get_rect(), border_radius=18)
                surface.blit(fill_surface, (opt_rect.x, opt_rect.y))
                
                # Border
                border_color = tuple(min(255, c + 60) for c in opt_color)
                pygame.draw.rect(surface, border_color, opt_rect, 2, border_radius=18)
                
                opt_text = self.font.render(option, True, (255, 255, 255))
                opt_text_rect = opt_text.get_rect(center=opt_rect.center)
                surface.blit(opt_text, opt_text_rect)
    
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.is_open = not self.is_open
            return True
        
        if self.is_open:
            for opt_rect, index in self.option_rects:
                if opt_rect.collidepoint(pos):
                    self.selected = index
                    self.is_open = False
                    return True
        
        return False

class LocationDropdown:
    def __init__(self, x, y, width, height, locations, default=0, color=(52, 152, 219)):
        self.rect = pygame.Rect(x, y, width, height)
        self.locations = locations  
        self.selected = default
        self.color = color
        self.hover_color = tuple(min(255, c + 30) for c in color)
        self.is_open = False
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 16)
        self.option_rects = []
        
    def draw(self, surface):
        current_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        
        for i in range(4, 0, -1):
            glow_rect = self.rect.inflate(i * 2, i * 2)
            glow_alpha = 15 * (5 - i)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_color = (*current_color, glow_alpha)
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=20)
            surface.blit(glow_surface, (glow_rect.x, glow_rect.y))
        
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (20, 25, 35, 180), bg_surface.get_rect(), border_radius=18)
        surface.blit(bg_surface, (self.rect.x, self.rect.y))

        fill_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(fill_surface, (*current_color, 100), fill_surface.get_rect(), border_radius=18)
        surface.blit(fill_surface, (self.rect.x, self.rect.y))
        
        border_color = tuple(min(255, c + 60) for c in current_color)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=18)
        

        text = self.locations[self.selected]
        if len(text) > 15:
            text = text[:12] + "..."
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        arrow = "▼" if not self.is_open else "▲"
        arrow_surface = self.font.render(arrow, True, (255, 255, 255))
        surface.blit(arrow_surface, (self.rect.right - 20, self.rect.y + 10))

        if self.is_open:
            self.option_rects = []
            for i, location in enumerate(self.locations):
                opt_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height * (i + 1), 
                                      self.rect.width, self.rect.height)
                self.option_rects.append((opt_rect, i))

                mouse_pos = pygame.mouse.get_pos()
                if opt_rect.collidepoint(mouse_pos):
                    opt_color = self.hover_color
                elif i == self.selected:
                    opt_color = tuple(max(0, c - 30) for c in self.color)
                else:
                    opt_color = self.color

                bg_surface = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(bg_surface, (20, 25, 35, 180), bg_surface.get_rect(), border_radius=18)
                surface.blit(bg_surface, (opt_rect.x, opt_rect.y))

                fill_surface = pygame.Surface((opt_rect.width, opt_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(fill_surface, (*opt_color, 100), fill_surface.get_rect(), border_radius=18)
                surface.blit(fill_surface, (opt_rect.x, opt_rect.y))

                border_color = tuple(min(255, c + 60) for c in opt_color)
                pygame.draw.rect(surface, border_color, opt_rect, 2, border_radius=18)
                
                opt_text = self.font.render(location, True, (255, 255, 255))
                opt_text_rect = opt_text.get_rect(center=opt_rect.center)
                surface.blit(opt_text, opt_text_rect)
    
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.is_open = not self.is_open
            return False  
        
        if self.is_open:
            for opt_rect, index in self.option_rects:
                if opt_rect.collidepoint(pos):
                    old_selected = self.selected
                    self.selected = index
                    self.is_open = False
                    return old_selected != index  
        
        return False
    
    def get_selected_location(self):
        return self.locations[self.selected]

class ButtonManager:
    def __init__(self, width, height, location_names):
        self.width = width
        self.height = height
        self.buttons = {}
        self.start_location_dropdown = None
        self.dest_location_dropdown = None
        self.obstacle_dropdown = None
        self.building_dropdown = None
        self.algorithm_dropdown = None
        
        self._create_buttons(location_names)
    
    def _create_buttons(self, location_names):
        button_width = 120
        button_height = 35
        
        # Position buttons in 2 rows on the right side
        row1_y = 110
        row2_y = 155
        
        spacing = 135

        start_x = self.width - (4 * spacing) - 50 - spacing  
        
        # Title row position 
        title_row_y = self.height - 145  
        run_button_x = self.width - button_width - 200  
        
        self.buttons = {
            'set_start': Button(start_x, row1_y, button_width, button_height, 'Set Start', (255, 200, 50)),  # Yellow
            'clear': Button(start_x + spacing * 3, row1_y, button_width, button_height, 'Clear Grid', (231, 76, 60)),  # Red
            'set_goal': Button(start_x, row2_y, button_width, button_height, 'Set Goal', (142, 68, 173)),  # Purple
            'load_map': Button(start_x + spacing * 3, row2_y, button_width, button_height, 'Load Map', (52, 152, 219)),  # Sky Blue
            'run': Button(run_button_x, title_row_y, button_width, button_height, 'RUN PATH', (46, 204, 113)),  # Green
        }
        
        # Location dropdowns
        self.start_location_dropdown = LocationDropdown(start_x + spacing, row1_y, button_width, button_height, 
                                                       location_names, default=0, color=(255, 200, 50))  # Yellow - Row 1
        self.dest_location_dropdown = LocationDropdown(start_x + spacing, row2_y, button_width, button_height, 
                                                      location_names, default=1, color=(142, 68, 173))  # Purple - Row 2
        
        # Obstacle/Building dropdown - Row 1
        self.obstacle_dropdown = Dropdown(start_x + spacing * 2, row1_y, button_width, button_height, 
                                         ['Building', 'Car'], default=0, color=(127, 140, 141))  # Gray
        
        # Algorithm dropdown - Row 2
        self.algorithm_dropdown = Dropdown(start_x + spacing * 2, row2_y, button_width, button_height, 
                                          ['Dijkstra', 'A* Algorithm'], default=1, color=(70, 130, 180))  # Blue
        
        # Building generation dropdown - Row 3 (new row below the existing buttons)
        row3_y = 200
        self.building_dropdown = Dropdown(start_x, row3_y, button_width, button_height, 
                                         ['Random', 'Recursive'], default=0, color=(230, 126, 34))  # Orange
    
    def draw(self, surface):
        for button in self.buttons.values():
            button.draw(surface)
        
        # Drawing dropdowns
        dropdowns = [
            self.start_location_dropdown,
            self.dest_location_dropdown,
            self.obstacle_dropdown,
            self.building_dropdown,
            self.algorithm_dropdown
        ]
        
        for dropdown in dropdowns:
            if not dropdown.is_open:
                dropdown.draw(surface)
        
        for dropdown in dropdowns:
            if dropdown.is_open:
                dropdown.draw(surface)
    
    def handle_click(self, pos, visualizer):
        if self.start_location_dropdown.handle_click(pos):
            selected_loc = self.start_location_dropdown.get_selected_location()
            print(f"Start location selected: {selected_loc}")
            visualizer.selected_start_location = selected_loc
            start_row = random.randint(5, 18)
            start_col = random.randint(15, 27)  
            visualizer.grid.set_start(0, start_row, start_col)
            visualizer.vehicle.position = [0, start_row, start_col]
            return True
        
        if self.dest_location_dropdown.handle_click(pos):
            selected_loc = self.dest_location_dropdown.get_selected_location()
            print(f"Destination selected: {selected_loc}")
            visualizer.selected_end_location = selected_loc
            end_row = random.randint(15, 30)
            end_col = random.randint(15, 27)  
            visualizer.grid.set_goal(0, end_row, end_col)
            return True
        
        if self.obstacle_dropdown.handle_click(pos):
            if self.obstacle_dropdown.selected == 0:
                visualizer.obstacle_type = 'building'
                visualizer.mode = 'obstacle'
                print("Obstacle mode: Building")
            else:
                visualizer.obstacle_type = 'car'
                visualizer.mode = 'obstacle'
                print("Obstacle mode: Car")
            return True

        if self.building_dropdown.handle_click(pos):
            visualizer.grid.reset()
            use_recursive = (self.building_dropdown.selected == 1)
            visualizer.grid.generate_buildings(use_recursive=use_recursive)
            method = "Recursive" if use_recursive else "Iterative"
            print(f"Buildings generated using {method} method")
            visualizer.grid.set_start(0, 2, 2)
            visualizer.grid.set_goal(0, visualizer.rows - 3, visualizer.cols - 3)
            return True

        if self.algorithm_dropdown.handle_click(pos):
            
            if self.algorithm_dropdown.selected == 0:
                visualizer.algorithm = 'dijkstra'
            else:
                visualizer.algorithm = 'a_star'
            return True

        for name, button in self.buttons.items():
            if button.rect.collidepoint(pos):
                if name == 'set_start':
                    visualizer.mode = 'start'
                elif name == 'set_goal':
                    visualizer.mode = 'goal'
                elif name == 'load_map':
                    
                    visualizer.load_osm_map()
                elif name == 'run':
                    visualizer.run_pathfinding()
                elif name == 'clear':
                    visualizer.grid.reset()
                    visualizer.vehicle.reset()
                    visualizer.metrics = {}
                    visualizer.osm_loaded = False
                    visualizer.animation_explored = []
                    visualizer.animation_final_path = []
                return True
        return False
    
    def handle_event(self, event):
        for button in self.buttons.values():
            button.handle_event(event)
