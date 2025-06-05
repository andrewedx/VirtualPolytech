import numpy as np
from entities.billboard import Billboard
from core.constants import ENTITY_TYPE

class UIManager:
    """Manages UI/HUD elements that are rendered in 3D space but attached to the camera"""
    
    def __init__(self):
        # Create UI elements
        self.interaction_prompt = Billboard([0, 0, 0])  # Position will be updated based on camera
        self.active_elements = set()  # Track which UI elements should be visible
        
    def update(self, dt: float, camera_pos: np.ndarray, camera_view: np.ndarray):
        """Update UI element positions based on camera"""
        if "interaction_prompt" in self.active_elements:
            # Extract camera orientation from view matrix
            # Note: View matrix is inverted, so we need to transpose and negate
            camera_forward = -camera_view[:3, 2]  # Third column is forward direction (negated)
            camera_up = camera_view[:3, 1]       # Second column is up direction
            camera_right = camera_view[:3, 0]    # First column is right direction
            
            # Position prompt in front of camera
            offset = camera_forward * 2.0  # 2 units in front
            offset += camera_up  * 0.3  # 0.3 units up
            
            # Update prompt position
            self.interaction_prompt.position = camera_pos + offset
            
            # Update prompt orientation to face camera
            self.interaction_prompt.update(dt, camera_pos)
    
    def show_interaction_prompt(self):
        """Make the interaction prompt visible"""
        self.active_elements.add("interaction_prompt")
    
    def hide_interaction_prompt(self):
        """Hide the interaction prompt"""
        self.active_elements.discard("interaction_prompt")  # Use discard instead of remove to avoid KeyError
    
    def get_renderable_elements(self) -> dict:
        """Return currently visible UI elements for rendering"""
        renderables = {}
        
        # Add interaction prompt if active
        if "interaction_prompt" in self.active_elements:
            renderables[ENTITY_TYPE["PROMPT"]] = [self.interaction_prompt]
        
        return renderables 