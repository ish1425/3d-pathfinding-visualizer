
import sys

def run_3d_gui():
    try:
        from visualizer_3d import Pathfinding3DVisualizer
        print("Starting 3D pathfinding visualizer with vehicle navigation...")
        print("\n✓ Features:")
        print("  - 3D Isometric view")
        print("  - GUI Buttons")
        print("  - Animated vehicle navigation")
        print("  - OpenStreetMap integration")
        print("  - Multi-level pathfinding")
        print("  - Full 3D camera rotation")
        print("\nStarting 3D GUI...")
        
        visualizer = Pathfinding3DVisualizer(rows=35, cols=35, height=5)
        visualizer.run()
    except ImportError as e:
        print(f"Error: {e}")
        print("pygame is required for GUI mode.")
        print("Install it with: pip install pygame")
        sys.exit(1)

def main():
    """Main entry point"""
    run_3d_gui()

if __name__ == "__main__":
    main()
