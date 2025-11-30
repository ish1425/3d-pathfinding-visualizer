
import pygame
import math
import time
import requests
from io import BytesIO
from PIL import Image, ImageEnhance

class OSMMapLoader:    
    DUBAI_LOCATIONS = {
        'Home': (25.2048, 55.2708),  
        'Dubai Mall': (25.1972, 55.2796),
        'Burj Khalifa': (25.1972, 55.2744),
        'Dubai Marina': (25.0808, 55.1420),
        'Palm Jumeirah': (25.1124, 55.1390),
        'Gold Souk': (25.2698, 55.2971),
        'Dubai Creek': (25.2631, 55.3297),
        'Mall of Emirates': (25.1183, 55.2007),
        'JBR Beach': (25.0772, 55.1326)
    }
    
    @staticmethod
    def get_location_names():
        return list(OSMMapLoader.DUBAI_LOCATIONS.keys())
    
    @staticmethod
    def load_map_for_locations(start_location, end_location, grid_size=35):
        if start_location not in OSMMapLoader.DUBAI_LOCATIONS or end_location not in OSMMapLoader.DUBAI_LOCATIONS:
            print(f"✗ Invalid locations: {start_location}, {end_location}")
            return None, None, None
        
        start_lat, start_lon = OSMMapLoader.DUBAI_LOCATIONS[start_location]
        end_lat, end_lon = OSMMapLoader.DUBAI_LOCATIONS[end_location]
        
        # center point between the two locations
        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2
        
        # distance to determine appropriate zoom level
        lat_diff = abs(end_lat - start_lat)
        lon_diff = abs(end_lon - start_lon)
        max_diff = max(lat_diff, lon_diff)
        
        # Adjust zoom based on distance
        if max_diff < 0.01:
            zoom = 15
        elif max_diff < 0.05:
            zoom = 14
        else:
            zoom = 13
        
        print(f"   Loading map: {start_location} → {end_location}")
        print(f"   Zoom level: {zoom}, Center: ({center_lat:.4f}, {center_lon:.4f})")
        
        try:
            # Convert center coordinates to tile numbers
            n = 2.0 ** zoom
            center_xtile = int((center_lon + 180.0) / 360.0 * n)
            center_ytile = int((1.0 - math.log(math.tan(math.radians(center_lat)) + (1 / math.cos(math.radians(center_lat)))) / math.pi) / 2.0 * n)
            
            # Fetch a 6x6 grid of tiles
            tiles = []
            print("   Downloading map tiles...", end="", flush=True)
            for dy in [-3, -2, -1, 0, 1, 2]:
                row_tiles = []
                for dx in [-3, -2, -1, 0, 1, 2]:
                    tile_url = f"https://tile.openstreetmap.org/{zoom}/{center_xtile + dx}/{center_ytile + dy}.png"
                    try:
                        response = requests.get(tile_url, timeout=10, headers={'User-Agent': 'PathfindingVisualizer/1.0'})
                        if response.status_code == 200:
                            tile_img = Image.open(BytesIO(response.content))
                            row_tiles.append(tile_img)
                        else:
                            row_tiles.append(Image.new('RGB', (256, 256), (220, 220, 220)))
                    except:
                        row_tiles.append(Image.new('RGB', (256, 256), (220, 220, 220)))
                    time.sleep(0.05)
                tiles.append(row_tiles)
            print(" ✓")
            
            full_width = 256 * 6
            full_height = 256 * 6
            combined_image = Image.new('RGB', (full_width, full_height))
            
            for row_idx, row in enumerate(tiles):
                for col_idx, tile in enumerate(row):
                    combined_image.paste(tile, (col_idx * 256, row_idx * 256))
            
            # pixel positions of start and end on the full image
            def lat_lon_to_pixel(lat, lon, zoom, ref_tile_x, ref_tile_y):
                n = 2.0 ** zoom
                x_tile = (lon + 180.0) / 360.0 * n
                y_tile = (1.0 - math.log(math.tan(math.radians(lat)) + (1 / math.cos(math.radians(lat)))) / math.pi) / 2.0 * n

                rel_x = (x_tile - (ref_tile_x - 3)) * 256
                rel_y = (y_tile - (ref_tile_y - 3)) * 256
                return int(rel_x), int(rel_y)
            
            start_px, start_py = lat_lon_to_pixel(start_lat, start_lon, zoom, center_xtile, center_ytile)
            end_px, end_py = lat_lon_to_pixel(end_lat, end_lon, zoom, center_xtile, center_ytile)
            
            # Cropping to center portion
            crop_size = 1200
            left = (full_width - crop_size) // 2
            top = (full_height - crop_size) // 2
            combined_image = combined_image.crop((left, top, left + crop_size, top + crop_size))
            
            # Adjusting pixel positions after crop
            start_px -= left
            start_py -= top
            end_px -= left
            end_py -= top
            
            # Applying enhancements
            enhancer = ImageEnhance.Contrast(combined_image)
            combined_image = enhancer.enhance(1.4)
            enhancer = ImageEnhance.Sharpness(combined_image)
            combined_image = enhancer.enhance(2.0)
            
            # Converting to pygame surface
            mode = combined_image.mode
            size = combined_image.size
            data = combined_image.tobytes()
            osm_surface = pygame.image.fromstring(data, size, mode)
            
            # Converting pixel positions to grid positions
            start_grid_col = int((start_px / crop_size) * grid_size)
            start_grid_row = int((start_py / crop_size) * grid_size)
            end_grid_col = int((end_px / crop_size) * grid_size)
            end_grid_row = int((end_py / crop_size) * grid_size)
            
            start_grid_col = max(0, min(grid_size - 1, start_grid_col))
            start_grid_row = max(0, min(grid_size - 1, start_grid_row))
            end_grid_col = max(0, min(grid_size - 1, end_grid_col))
            end_grid_row = max(0, min(grid_size - 1, end_grid_row))
            
            print(f"✓ Map loaded successfully!")
            print(f"   {start_location}: grid position ({start_grid_row}, {start_grid_col})")
            print(f"   {end_location}: grid position ({end_grid_row}, {end_grid_col})")
            
            return osm_surface, (0, start_grid_row, start_grid_col), (0, end_grid_row, end_grid_col)
                
        except Exception as e:
            print(f"✗ Error loading map: {e}")
            return None, None, None
    
    @staticmethod
    def load_dubai_map():
        lat, lon = 25.170174, 55.287915
        zoom = 13 
        
        print(f"Loading Dubai map at coordinates: ({lat}, {lon}), zoom: {zoom}")
        
        try:
            print(f"Fetching map tiles from OpenStreetMap...")
            
            # Converting coordinates to tile numbers
            n = 2.0 ** zoom
            xtile = int((lon + 180.0) / 360.0 * n)
            ytile = int((1.0 - math.log(math.tan(math.radians(lat)) + (1 / math.cos(math.radians(lat)))) / math.pi) / 2.0 * n)
            
            print(f"Center tile: ({xtile}, {ytile}) at zoom {zoom}")
            
            # Fetching a 6x6 grid of tiles for ultra-high resolution
            tiles = []
            for dy in [-3, -2, -1, 0, 1, 2]:
                row_tiles = []
                for dx in [-3, -2, -1, 0, 1, 2]:
                    tile_url = f"https://tile.openstreetmap.org/{zoom}/{xtile + dx}/{ytile + dy}.png"
                    try:
                        response = requests.get(tile_url, timeout=10, headers={'User-Agent': 'PathfindingVisualizer/1.0'})
                        if response.status_code == 200:
                            tile_img = Image.open(BytesIO(response.content))
                            row_tiles.append(tile_img)
                        else:
                            row_tiles.append(Image.new('RGB', (256, 256), (220, 220, 220)))
                    except:
                        row_tiles.append(Image.new('RGB', (256, 256), (220, 220, 220)))
                    time.sleep(0.05)  
                tiles.append(row_tiles)
            
            full_width = 256 * 6
            full_height = 256 * 6
            combined_image = Image.new('RGB', (full_width, full_height))
            
            for row_idx, row in enumerate(tiles):
                for col_idx, tile in enumerate(row):
                    combined_image.paste(tile, (col_idx * 256, row_idx * 256))

            crop_size = 1200  
            left = (full_width - crop_size) // 2
            top = (full_height - crop_size) // 2
            combined_image = combined_image.crop((left, top, left + crop_size, top + crop_size))
            
            enhancer = ImageEnhance.Contrast(combined_image)
            combined_image = enhancer.enhance(1.4)
            enhancer = ImageEnhance.Sharpness(combined_image)
            combined_image = enhancer.enhance(2.0)
            
            # Converting PIL image to pygame surface
            mode = combined_image.mode
            size = combined_image.size
            data = combined_image.tobytes()
            
            osm_surface = pygame.image.fromstring(data, size, mode)
            print("✓ Dubai map loaded successfully!")
            
            return osm_surface
                
        except Exception as e:
            print(f"✗ Error loading map: {e}")
            return None
    
    @staticmethod
    def create_fallback_map(grid):
        print("Creating fallback street grid...")
        street_spacing = 6
        street_width = 2
        
        rows = grid.grid.shape[1]
        cols = grid.grid.shape[2]
        
        # Horizontal streets
        for i in range(0, rows, street_spacing):
            for row in range(i, min(i + street_width, rows)):
                for col in range(cols):
                    grid.terrain_costs[0, row, col] = 0.3
        
        # Vertical streets
        for i in range(0, cols, street_spacing):
            for col in range(i, min(i + street_width, cols)):
                for row in range(rows):
                    grid.terrain_costs[0, row, col] = 0.3
    
    @staticmethod
    def initialize_map(grid, rows, cols):
        grid.reset()
        osm_background = OSMMapLoader.load_dubai_map()
        
        if osm_background is None:
            OSMMapLoader.create_fallback_map(grid)
        
        grid.set_start(0, 2, 2)
        grid.set_goal(0, rows - 3, cols - 3)
        
        print("✓ Map reloaded successfully!")
        return osm_background
    
    @staticmethod
    def initialize_locations_map(grid, vehicle, start_loc, dest_loc, rows):
        print(f"\n{'='*60}")
        print(f"Loading route: {start_loc} → {dest_loc}")
        print(f"{'='*60}")
        
        grid.reset()
        vehicle.reset()       
        osm_map, start_pos, end_pos = OSMMapLoader.load_map_for_locations(start_loc, dest_loc, rows)
        
        if osm_map and start_pos and end_pos:
            start_z, start_row, start_col = start_pos
            end_z, end_row, end_col = end_pos
            
            grid.set_start(start_z, start_row, start_col)
            grid.set_goal(end_z, end_row, end_col)
            vehicle.position = [start_z, start_row, start_col]
            
            print(f"{'='*60}\n")
            return osm_map, start_loc, dest_loc, True
        else:
            print("✗ Failed to load map, falling back to default")
            return None, start_loc, dest_loc, False
