from entities.base import Entity
import numpy as np
import pyrr
from core.constants import GLOBAL_X, GLOBAL_Y, GLOBAL_Z

class Door(Entity):
    __slots__ = ("is_open", "speed", "angle_limit", "pivot_offset", "is_active", "base_angle", "direction")

    def __init__(self, position: list[float], eulers: list[float], pivot_offset: list[float] = None, direction: int = 1):
        super().__init__(position, eulers)
        # If pivot_offset is not provided, calculate it as -position + [0,0,0.5]
        if pivot_offset is None:
            # The pivot should be negative of the position plus the offset
            self.pivot_offset = -np.array(position, dtype=np.float32) + np.array([0, 0, 0.5], dtype=np.float32)
        else:
            self.pivot_offset = np.array(pivot_offset, dtype=np.float32)
        self.is_open = False
        self.speed = 1.0
        self.angle_limit = 90.0
        self.is_active = False
        self.base_angle = eulers[1]  # Store the initial angle
        self.direction = direction  # 1 for default rotation, -1 for opposite rotation

    def toggle(self):
        self.is_open = not self.is_open
        print(f"Door {'opened' if self.is_open else 'closed'}.")

    def update(self, dt: float, camera_pos: np.ndarray) -> None:
        # Check if player is close enough to interact
        dist = np.linalg.norm(camera_pos - self.position)
        was_active = self.is_active
        self.is_active = dist < 3.0

        # Update door animation
        direction = self.direction if self.is_open else -self.direction
        target_angle = self.base_angle + (self.angle_limit * self.direction) if self.is_open else self.base_angle
        angle_diff = target_angle - self.eulers[1]
        if abs(angle_diff) > 0.01:
            self.eulers[1] += direction * self.speed * dt
            self.eulers[1] = np.clip(
                self.eulers[1], 
                min(self.base_angle, self.base_angle + (self.angle_limit * self.direction)),
                max(self.base_angle, self.base_angle + (self.angle_limit * self.direction))
            )

    def get_model_transform(self) -> np.ndarray:
        """
        Compute the world transform for the door, rotating around a local-space pivot (hinge).
        """
        # Step 1: Move to pivot point
        T_pivot = pyrr.matrix44.create_from_translation(self.pivot_offset)
        
        # Step 2: Apply rotation (Z-Y-X)
        Rz = pyrr.matrix44.create_from_axis_rotation(GLOBAL_Z, np.radians(self.eulers[2]))
        Ry = pyrr.matrix44.create_from_axis_rotation(GLOBAL_Y, np.radians(self.eulers[1]))
        Rx = pyrr.matrix44.create_from_axis_rotation(GLOBAL_X, np.radians(self.eulers[0]))
        R = pyrr.matrix44.multiply(Rz, pyrr.matrix44.multiply(Ry, Rx))

        # Step 3: Move back from pivot
        T_unpivot = pyrr.matrix44.create_from_translation(-self.pivot_offset)

        # Step 4: Move to world position (this should be last)
        T_world = pyrr.matrix44.create_from_translation(self.position)

        # Final matrix: world * (pivot * rotation * unpivot)
        # This means: first do the pivot rotation, then move to world position
        return T_world @ (T_pivot @ R @ T_unpivot)



