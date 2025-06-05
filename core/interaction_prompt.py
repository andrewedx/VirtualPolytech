from entities.billboard import Billboard
from core.constants import ENTITY_TYPE
import numpy as np

class PromptBillboard(Billboard):
    """A specialized billboard for interaction prompts"""
    entity_type = ENTITY_TYPE["PROMPT"]

    def update(self, dt: float, camera_pos: np.ndarray) -> None:
        super().update(dt, camera_pos)
        print(f"Prompt billboard position: {self.position}, visible: {self.visible}")

class InteractionPrompt:
    """
    A singleton class that manages interaction prompts in the game.
    Shows a prompt when the player is near interactive objects.
    """
    def __init__(self):
        self.billboard = PromptBillboard([0, 0, 0])
        self.billboard.visible = False
        self.current_interactive = None
        print("InteractionPrompt initialized")

    def update(self, dt: float, camera_pos: np.ndarray, scene) -> None:
        """
        Updates the prompt position and visibility based on nearby interactive objects
        """
        print(f"\nUpdating interaction prompt. Camera at {camera_pos}")
        
        # Reset visibility
        self.billboard.visible = False
        self.current_interactive = None

        # Find closest active interactive object
        closest_dist = float('inf')
        
        # Check all interactive objects in scene
        for entity_type, entities in scene.entities.items():
            for entity in entities:
                if hasattr(entity, 'is_active'):
                    print(f"Checking entity: {type(entity).__name__} at {entity.position}, is_active: {entity.is_active}")
                    if entity.is_active:
                        dist = np.linalg.norm(camera_pos - entity.position)
                        if dist < closest_dist:
                            closest_dist = dist
                            self.current_interactive = entity
                            self.billboard.visible = True
                            print(f"Found active entity at distance {dist}")

        # If we found an interactive object, position the prompt
        if self.billboard.visible:
            print("Setting prompt position")
            # Use camera's forward vector to position prompt
            camera = scene.player  # Get camera from scene
            self.billboard.position = camera_pos + camera.forwards * 0.8 + np.array([0, 0, -0.2], dtype=np.float32)  # Closer to camera and slightly less down
            self.billboard.update(dt, camera_pos)
        else:
            print("No active interactive objects found") 