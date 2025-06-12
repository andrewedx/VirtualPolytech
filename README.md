# 3D Graphics Project

A 3D graphics application built with Python and OpenGL, featuring a first-person camera system, dynamic lighting, and interactive elements.

Aimed to show a 3D model of Polytech Paris Saclay.

## Features

- First-person camera navigation
- Dynamic point lighting system with multiple light sources
- Interactive doors
- Skybox rendering
- Shadow mapping
- UI elements with billboarding
- Modern OpenGL (Core Profile 3.3) implementation

## Prerequisites

- Python 3.x
- GLFW
- PyOpenGL
- NumPy
- Pyrr (for matrix and vector operations)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install the required dependencies:
```bash
pip install numpy pyopengl glfw pyrr
```

## Controls

- **W/A/S/D** - Move forward/left/backward/right
- **SHIFT** - move faster
- **Q/E** - Move up/down
- **F** - Open/Close door
- **R** - Relaod Shader
- **L** - Toggle Shadows
- **Mouse** - Look around
- **TAB** - Toggle mouse capture
- **ESC** - Exit application

## Project Structure

```
.
├── core/
│   ├── app.py           # Main application control
│   ├── constants.py     # Global constants
│   ├── scene.py         # Scene management
│   └── ui_manager.py    # UI handling
├── entities/
│   ├── base.py         # Base entity class
│   ├── billboard.py    # Billboard implementation
│   ├── cube.py        # Cube entity
│   ├── door.py        # Interactive door
│   └── pointlight.py  # Point light source
├── graphics/
│   ├── engine.py      # Graphics rendering engine
│   ├── material.py    # Material system
│   ├── mesh.py        # Mesh handling
│   ├── shader.py      # Shader management
│   └── skybox.py      # Skybox implementation
└── utils/
    ├── colors.py      # Color utilities
    └── obj_loader.py  # 3D model loading

```

## Technical Features

### Graphics
- Modern OpenGL with core profile 3.3
- Shader-based rendering pipeline
- Dynamic shadow mapping
- Alpha blending support
- Texture mapping

### Lighting
- Multiple point light sources
- Light attenuation
- Dynamic light updates
- Configurable light colors and intensities

### Camera System
- First-person perspective
- Smooth movement and rotation

### Interactive Elements
- Door system with proximity detection
- UI prompts for interaction
- Billboard system for UI elements

## Development

### Adding New Entities

1. Create a new class in the `entities/` directory
2. Inherit from the `Entity` base class
3. Implement required methods:
   - `__init__`
   - `update`
   - `get_model_transform` (if needed)

Example:
```python
from entities.base import Entity

class NewEntity(Entity):
    def __init__(self, position, eulers):
        super().__init__(position, eulers)
        
    def update(self, dt, camera_pos):
        # Implementation here
        pass
```

### Adding New Lights

Create new PointLight instances in the scene:
```python
PointLight(
    position=[x, y, z],
    color=[r, g, b],
    strength=intensity
)
```

## Performance Considerations

- Light sources are limited and sorted by distance to camera
- Optimized shader uniforms caching
- Efficient vertex buffer management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

