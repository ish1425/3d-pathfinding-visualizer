# Intelligent Pathfinding Using Dijkstra and A* Search Algorithms

## 🎯 Project Overview

This project implements and compares two fundamental pathfinding algorithms:

**Dijkstra's Algorithm**: Guarantees shortest path

**A\* Search**: Uses heuristics to guide search toward the goal

## 📁 Project Structure

```
pathfinding/
├── main.py                           # Entry point for the application
├── visualizer_3d.py                  # 3D visualization engine
├── pathfinding_algorithms_3d.py      # Dijkstra & A* implementations
├── requirements.txt                  # Python dependencies
├── components/
│   ├── grid_environment_3d.py        # 3D grid management
│   ├── vehicle_3d.py                 # Vehicle movement & rendering
│   ├── ui_components.py              # UI buttons and controls
│   └── map_loader.py                 # OpenStreetMap integration
└── README.md
```

## 🗺️ Available Dubai Locations

The application includes OpenStreetMap integration for the following Dubai landmarks:

- **Home** (25.2048, 55.2708)
- **Dubai Mall** (25.1972, 55.2796)
- **Dubai Marina** (25.0808, 55.1420)
- **Dubai Creek** (25.2631, 55.3297)
- **Mall of Emirates** (25.1183, 55.2007)

## 💻 Usage

Launch the 3D visualization:
```bash
python main.py --3d
```

## ✨ Features
### 🚀 3D Visualization Mode

✅ 3D Isometric View with OrbitControls-style camera

✅ Vehicle Navigation: Cyan vehicle follows the computed path

✅ Multi-Level Navigation: 35×35×5 grid

✅ OpenStreetMap Integration: Dubai city maps

✅ Recursive Building Generation: Random or Recursive

✅ 3D Buildings: Multi-story obstacles

## 🚀 Installation

Python 3.7+ and pip required.

Install dependencies:
```bash
pip install -r requirements.txt
```

Or individually:
```bash
pip install pygame numpy matplotlib seaborn pandas
```

## 🎨 Visualization Colors

- **Green**: Start marker
- **Red**: Goal marker
- **Cyan**: Explored cells
- **Yellow**: Final path
- **Cyan Vehicle**: Moving vehicle

## 📄 License

MIT License

## 👤 Author

Ishika Vachheta



