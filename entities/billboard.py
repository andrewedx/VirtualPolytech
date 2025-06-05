from entities.base import Entity
from core.constants import ENTITY_TYPE
import numpy as np
import pyrr

class Billboard(Entity):
    """
        An object which always faces towards the camera
    """
    __slots__ = ("visible",)
    entity_type = ENTITY_TYPE["PROMPT"]

    def __init__(self, position: list[float]):
        """
            Initialize the billboard.

            Parameters:

                position: the position of the entity.
        """

        super().__init__(position, eulers=[0,0,0])
        self.visible = True
    
    def update(self, dt: float, camera_pos: np.ndarray) -> None:
        """
            Update the billboard.

            Parameters:

                dt: framerate correction factor.

                camera_pos: the position of the camera in the scene
        """

        self_to_camera = camera_pos - self.position
        self.eulers[2] = -np.degrees(np.arctan2(-self_to_camera[1], self_to_camera[0]))
        dist2d = pyrr.vector.length(self_to_camera)
        self.eulers[1] = -np.degrees(np.arctan2(self_to_camera[2], dist2d))
