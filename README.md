# Intelligent Pathfinding Using Dijkstra and A* Search Algorithms

A comprehensive Python implementation of pathfinding algorithms with **3D visualization**, **vehicle navigation**, **GUI buttons**, and **OpenStreetMap integration**.

🎯 Project Overview

This project implements and compares two fundamental pathfinding algorithms:

Dijkstra's Algorithm: Guarantees shortest path

A Search*: Uses heuristics to guide search toward the goal

✨ Features
🚀 3D Visualization Mode

✅ 3D Isometric View with OrbitControls-style camera

✅ Vehicle Navigation: Cyan vehicle follows the computed path

✅ Multi-Level Navigation: 35×35×5 grid

✅ OpenStreetMap Integration: Dubai city maps

✅ Recursive Building Generation: Iterative or Recursive

✅ Dense City Environment: 160-170 buildings

✅ 3D Buildings: Multi-story obstacles

📁 Project Structure

pathfinding/
├── main.py
├── pathfinding_algorithms_3d.py
├── grid_environment_3d.py
├── vehicle_3d.py
├── visualizer_3d.py
├── map_loader.py
├── requirements.txt
└── README.md

🚀 Installation

Python 3.7+ and pip required.

Install dependencies:
pip install -r requirements.txt

Or individually:
pip install pygame numpy matplotlib seaborn pandas

💻 Usage

Launch the 3D visualization:
python main.py

Key Features:

3D Isometric View: Full multi-level grid

Camera Controls: Right-click drag (rotate), mouse wheel (zoom)

Vehicle Animation: Cyan vehicle follows path

OSM Integration: Dubai city maps

Building Generation: Iterative or Recursive

Gradient UI background

Level Control: Switch height levels

Typical Performance (35×35×5 grid):

Dijkstra: Explores more nodes, slower

A*: Explores fewer nodes, faster


🎨 Visualization Colors

White: Walkable ground
Dark Gray: 3D obstacles
Green: Start marker
Red: Goal marker
Cyan: Explored cells
Yellow: Final path
Cyan Vehicle: Moving vehicle
Black: Grid lines
Blue Gradient: UI background

🌟 Features Completed

3D pathfinding ✓

Vehicle animation ✓

OSM integration ✓

Full 3D rotation ✓

Recursive building generation ✓

Dense city environment ✓

Modern gradient UI ✓

Proper rendering order ✓


🐛 Troubleshooting

Reduce grid/building size for performance

Ensure Python 3.7+ and dependencies

Verify all files in same directory

# 📚 References

1. Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs"
2. Hart, P. E.; Nilsson, N. J.; Raphael, B. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths"
3. Russell, S.; Norvig, P. (2020). "Artificial Intelligence: A Modern Approach"

## 📄 License

This project is created for educational purposes. Feel free to use, modify, and distribute for learning and teaching.

## 👨‍💻 Author

Created as part of project.

## 🙏 Acknowledgments

- Pygame community for visualization tools
- NumPy and Matplotlib for numerical computing and plotting
- Jupyter for interactive analysis environment

---

**Happy Pathfinding! 🎯🤖**
