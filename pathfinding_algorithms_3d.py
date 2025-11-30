
import heapq
import time
from typing import List, Tuple, Dict
from components.grid_environment_3d import Grid3DEnvironment

class Pathfinding3DAlgorithms:    
    def __init__(self, grid: Grid3DEnvironment):
        self.grid = grid
        self.reset_metrics()
    
    def reset_metrics(self):
        self.nodes_explored = 0
        self.path_length = 0
        self.execution_time = 0
        self.explored_nodes = []
    
    def get_neighbors(self, node: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        z, row, col = node
        neighbors = []
        
        # 6-directional movement: up, down, left, right, forward, backward
        directions = [
            (0, -1, 0),   # up
            (0, 1, 0),    # down
            (0, 0, -1),   # left
            (0, 0, 1),    # right
            (-1, 0, 0),   # lower level
            (1, 0, 0),    # upper level
            # Diagonals on same level
            (0, -1, -1), (0, -1, 1),
            (0, 1, -1), (0, 1, 1),
        ]
        
        for dz, dr, dc in directions:
            new_z, new_row, new_col = z + dz, row + dr, col + dc
            # Check if within bounds and not an obstacle
            if (0 <= new_z < self.grid.height and
                0 <= new_row < self.grid.rows and 
                0 <= new_col < self.grid.cols and 
                not self.grid.is_obstacle(new_z, new_row, new_col)):
                neighbors.append((new_z, new_row, new_col))
        
        return neighbors
    
    def heuristic(self, node1: Tuple[int, int, int], node2: Tuple[int, int, int]) -> float:
        return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1]) + abs(node1[2] - node2[2])
    
    def reconstruct_path(self, came_from: Dict, current: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
    def dijkstra(self, start: Tuple[int, int, int], goal: Tuple[int, int, int]) -> Tuple[List[Tuple[int, int, int]], Dict]:
        self.reset_metrics()
        start_time = time.time()      
        pq = [(0, start)]
        came_from = {}
        cost_so_far = {start: 0}
        visited = set()
        
        while pq:
            current_cost, current = heapq.heappop(pq)
            
            if current not in visited:
                self.nodes_explored += 1
                self.explored_nodes.append(current)
                visited.add(current)
            
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                self.path_length = len(path)
                self.execution_time = time.time() - start_time
                return path, self._get_metrics()
            
            if current_cost > cost_so_far.get(current, float('inf')):
                continue
            
            for neighbor in self.get_neighbors(current):
                new_cost = current_cost + self.grid.get_cost(neighbor[0], neighbor[1], neighbor[2])
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, neighbor))
                    came_from[neighbor] = current
        
        self.execution_time = time.time() - start_time
        return [], self._get_metrics()
    
    def a_star(self, start: Tuple[int, int, int], goal: Tuple[int, int, int]) -> Tuple[List[Tuple[int, int, int]], Dict]:
        self.reset_metrics()
        start_time = time.time()
        
        pq = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        visited = set()
        
        while pq:
            current_f, current = heapq.heappop(pq)
            
            if current not in visited:
                self.nodes_explored += 1
                self.explored_nodes.append(current)
                visited.add(current)
            
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                self.path_length = len(path)
                self.execution_time = time.time() - start_time
                return path, self._get_metrics()
            
            if current_f > f_score.get(current, float('inf')):
                continue
            
            for neighbor in self.get_neighbors(current):
                tentative_g = g_score[current] + self.grid.get_cost(neighbor[0], neighbor[1], neighbor[2])
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(pq, (f_score[neighbor], neighbor))
        
        self.execution_time = time.time() - start_time
        return [], self._get_metrics()
    
    def _get_metrics(self) -> Dict:
        return {
            'nodes_explored': self.nodes_explored,
            'path_length': self.path_length,
            'execution_time': self.execution_time,
            'explored_nodes': self.explored_nodes.copy()
        }
