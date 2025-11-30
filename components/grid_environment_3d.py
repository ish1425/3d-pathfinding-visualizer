
import random
import numpy as np
from typing import Tuple, List, Set

class Grid3DEnvironment:
    # Cell types
    EMPTY = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3
    PATH = 4
    EXPLORED = 5
    CAR = 6  # Car obstacle type
    
    def __init__(self, rows: int = 30, cols: int = 30, height: int = 5):
        self.rows = rows
        self.cols = cols
        self.height = height
        self.grid = np.zeros((height, rows, cols), dtype=int)
        self.terrain_costs = np.ones((height, rows, cols), dtype=float)
        self.elevation = np.zeros((rows, cols), dtype=float)  
        self.start = None
        self.goal = None
        self.obstacles = set()
        self.cars = set()  
    
    def reset(self):
        self.grid = np.zeros((self.height, self.rows, self.cols), dtype=int)
        self.terrain_costs = np.ones((self.height, self.rows, self.cols), dtype=float)
        self.elevation = np.zeros((self.rows, self.cols), dtype=float)
        self.start = None
        self.goal = None
        self.obstacles = set()
        self.cars = set()
    
    def set_start(self, z: int, row: int, col: int):
        if self.start:
            old_z, old_row, old_col = self.start
            if self.grid[old_z, old_row, old_col] == self.START:
                self.grid[old_z, old_row, old_col] = self.EMPTY
        
        self.start = (z, row, col)
        self.grid[z, row, col] = self.START
    
    def set_goal(self, z: int, row: int, col: int):
        if self.goal:
            old_z, old_row, old_col = self.goal
            if self.grid[old_z, old_row, old_col] == self.GOAL:
                self.grid[old_z, old_row, old_col] = self.EMPTY
        
        self.goal = (z, row, col)
        self.grid[z, row, col] = self.GOAL
    
    def add_obstacle(self, z: int, row: int, col: int):
        if (z, row, col) != self.start and (z, row, col) != self.goal:
            self.grid[z, row, col] = self.OBSTACLE
            self.obstacles.add((z, row, col))
    
    def add_car(self, z: int, row: int, col: int):
        if (z, row, col) != self.start and (z, row, col) != self.goal and z == 0:
            self.grid[z, row, col] = self.CAR
            self.cars.add((z, row, col))
    
    def remove_obstacle(self, z: int, row: int, col: int):
        if (z, row, col) in self.obstacles:
            self.grid[z, row, col] = self.EMPTY
            self.obstacles.discard((z, row, col))
            self.terrain_costs[z, row, col] = 1.0
        if (z, row, col) in self.cars:
            self.grid[z, row, col] = self.EMPTY
            self.cars.discard((z, row, col))
    
    def is_obstacle(self, z: int, row: int, col: int) -> bool:
        cell_type = self.grid[z, row, col]
        return cell_type == self.OBSTACLE or cell_type == self.CAR
    
    def get_cost(self, z: int, row: int, col: int) -> float:
        # Add elevation cost
        base_cost = self.terrain_costs[z, row, col]
        elevation_cost = abs(self.elevation[row, col] - z) * 0.5
        return base_cost + elevation_cost
    
    def set_terrain_cost(self, z: int, row: int, col: int, cost: float):
        if not self.is_obstacle(z, row, col):
            self.terrain_costs[z, row, col] = cost
    
    def generate_random_obstacles(self, density: float = 0.15):
        num_obstacles = int(self.height * self.rows * self.cols * density)
        
        for _ in range(num_obstacles):
            z = random.randint(0, self.height - 1)
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)

            if (z, row, col) != self.start and (z, row, col) != self.goal:
                self.add_obstacle(z, row, col)
    
    def generate_buildings(self, use_recursive=False):
        if use_recursive:
            num_edge_buildings = random.randint(10, 12)
            total_edge = num_edge_buildings * 4  # 4 edges
            center_buildings = random.randint(160, 170) - total_edge  
            
            self._place_perimeter_buildings(num_edge_buildings)
            self._generate_buildings_recursive_center(5, self.rows - 6, 5, self.cols - 6, target=center_buildings)
        else:
            num_buildings = random.randint(8, 15)
            
            for _ in range(num_buildings):
                base_row = random.randint(2, self.rows - 3)
                base_col = random.randint(2, self.cols - 3)
                building_height = random.randint(1, self.height)
        
                for z in range(building_height):
                    if (z, base_row, base_col) != self.start and (z, base_row, base_col) != self.goal:
                        self.add_obstacle(z, base_row, base_col)
    
    def _place_perimeter_buildings(self, buildings_per_edge=10):
        min_r, max_r = 2, self.rows - 3
        min_c, max_c = 2, self.cols - 3
        
        for i in range(buildings_per_edge):
            col = min_c + int((max_c - min_c) * i / buildings_per_edge) + random.randint(0, 2)
            col = min(col, max_c)
            building_height = random.randint(2, self.height)
            self._build_column_recursive(min_r, col, 0, building_height)

        for i in range(buildings_per_edge):
            col = min_c + int((max_c - min_c) * i / buildings_per_edge) + random.randint(0, 2)
            col = min(col, max_c)
            building_height = random.randint(2, self.height)
            self._build_column_recursive(max_r, col, 0, building_height)

        for i in range(buildings_per_edge):
            row = min_r + int((max_r - min_r) * i / buildings_per_edge) + random.randint(0, 2)
            row = min(row, max_r)
            building_height = random.randint(2, self.height)
            self._build_column_recursive(row, min_c, 0, building_height)

        for i in range(buildings_per_edge):
            row = min_r + int((max_r - min_r) * i / buildings_per_edge) + random.randint(0, 2)
            row = min(row, max_r)
            building_height = random.randint(2, self.height)
            self._build_column_recursive(row, max_c, 0, building_height)
    
    def _generate_buildings_recursive_center(self, min_row, max_row, min_col, max_col, target=40, count=0):
        if count >= target:
            return count     
        if max_row - min_row < 3 or max_col - min_col < 3:
            return count

        row = random.randint(min_row, max_row)
        col = random.randint(min_col, max_col)
        building_height = random.randint(1, 3)
        
        self._build_column_recursive(row, col, 0, building_height)
        count += 1
        
        if count >= target:
            return count

        mid_row = (min_row + max_row) // 2
        mid_col = (min_col + max_col) // 2
 
        count = self._generate_buildings_recursive_center(min_row, mid_row, min_col, mid_col, target, count)
        if count >= target:
            return count
            
        count = self._generate_buildings_recursive_center(min_row, mid_row, mid_col, max_col, target, count)
        if count >= target:
            return count
            
        count = self._generate_buildings_recursive_center(mid_row, max_row, min_col, mid_col, target, count)
        if count >= target:
            return count
            
        count = self._generate_buildings_recursive_center(mid_row, max_row, mid_col, max_col, target, count)
        count = self._generate_buildings_recursive_center(mid_row, max_row, mid_col, max_col, target, count)
        
        return count
    def _build_column_recursive(self, row, col, current_z, target_height):
        if current_z >= target_height:
            return
        
        if (current_z, row, col) != self.start and (current_z, row, col) != self.goal:
            self.add_obstacle(current_z, row, col)
        
        self._build_column_recursive(row, col, current_z + 1, target_height)
    
    
    def clear_path_visualization(self):
        for z in range(self.height):
            for row in range(self.rows):
                for col in range(self.cols):
                    if self.grid[z, row, col] in [self.PATH, self.EXPLORED]:
                        self.grid[z, row, col] = self.EMPTY
        
        if self.start:
            self.grid[self.start[0], self.start[1], self.start[2]] = self.START
        if self.goal:
            self.grid[self.goal[0], self.goal[1], self.goal[2]] = self.GOAL
    
    def mark_explored(self, nodes: List[Tuple[int, int, int]]):
        marked = 0
        for z, row, col in nodes:
            if self.grid[z, row, col] == self.EMPTY:
                self.grid[z, row, col] = self.EXPLORED
                marked += 1
        print(f"  Marked {marked} out of {len(nodes)} cells as explored")
    
    def mark_path(self, path: List[Tuple[int, int, int]]):
        for z, row, col in path:
            if (z, row, col) != self.start and (z, row, col) != self.goal:
                self.grid[z, row, col] = self.PATH
