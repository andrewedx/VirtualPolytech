import numpy as np
import pyrr
from entities.cube import Cube
from entities.billboard import Billboard
from entities.pointlight import PointLight
from entities.base import Entity
from entities.door import Door
from core.constants import *
from core.ui_manager import UIManager




class Camera(Entity):
    """
        A first person camera.
    """
    __slots__ = ("forwards", "right", "up")


    def __init__(self, position: list[float]):
        """
            Initialize the camera.

            Parameters:

                position: the camera's position
        """

        super().__init__(position, eulers = [0,0,0])
        self.update(0)
    
    def update(self, dt: float) -> None:
        """
            Update the camera.

            Parameters:

                dt: framerate correction factor
        """

        theta = self.eulers[2]
        phi = self.eulers[1]

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(phi))
            ],
            dtype = np.float32
        )

        self.right = np.cross(self.forwards, GLOBAL_Z)

        self.up = np.cross(self.right, self.forwards)

    def get_view_transform(self) -> np.ndarray:
        """
            Returns the camera's world to view
            transformation matrix.
        """

        return pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, dtype = np.float32)
    
    def move(self, d_pos) -> None:
        """
            Move by the given amount in the (forwards, right, up) vectors.
        """

        self.position += d_pos[0] * self.forwards \
                        + d_pos[1] * self.right \
                        + d_pos[2] * self.up
    

    
    def spin(self, d_eulers) -> None:
        """
            Spin the camera by the given amount about the (x, y, z) axes.
        """

        self.eulers += d_eulers

        self.eulers[0] %= 360
        self.eulers[1] = min(89, max(-89, self.eulers[1]))
        self.eulers[2] %= 360

class Scene:
    """
        Manages all objects and coordinates their interactions in the game world.
    """
    __slots__ = ("entities", "player", "lights", "ui_manager")


    def __init__(self):
        """
            Initialize the scene with a root SceneNode.
        """
        self.ui_manager = UIManager()

        door_to_open = {
            "pos": [18.60, 31.418 ,5.05],
            "eulers":[90,90,0]
            
        }


        self.entities: dict[int, list[Entity]] = {
            ENTITY_TYPE["CUBE"]: [
                Cube(position = [0,0,0], eulers = [90,0,-90]),
            ],
            ENTITY_TYPE["DOOR"]: [
                Door(position = door_to_open["pos"], eulers = door_to_open["eulers"], direction = -1),
            ]

        }

        self.lights: list[PointLight] = [
            PointLight(
                position = [1, 1, 1],
                color = [1, 1, 1],
                strength = 7),

            PointLight(
                position = [-6,30,8],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-6,27,8],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-6,33,8],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-10,30,10],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-10,27,10],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-10,33,10],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-14,30,10],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-14,27,10],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            PointLight(
                position = [-14,33,10],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),

            ## B007
            PointLight(
                position = [-4,-24,3],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),

            ## B009
            PointLight(
                position = [-4,-33,3],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            
            ## B020
            PointLight(
                position = [-15,-33,3],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            
            ## B016
            PointLight(
                position = [-15,-13,3],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),
            
            ## B014
            PointLight(
                position = [-15, 1,3],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),

            ## A
            PointLight(
                position = [29, 26,6],
                color = [1.0, 1.0, 1.0],
                strength = 8.0),

            ## A103
            PointLight(
                position = [13.5, 34,6],
                color = [1.0, 1.0, 1.0],
                strength = 8.0)


        ]

        self.player = Camera(
            position = [-26.1, 30.15 , 1.5]
        )

    def update(self, dt: float) -> None:
        """
            Update all objects in the scene.

            Parameters:
                dt: framerate correction factor
        """
        # Update player first to get latest view matrix
        self.player.update(dt)
        view_matrix = self.player.get_view_transform()
        
        # Print camera position
        print(f"Camera position: {self.player.position}")

        # Check if any doors are active to show/hide prompt
        any_door_active = False
        for door in self.entities.get(ENTITY_TYPE["DOOR"], []):
            door.update(dt, self.player.position)
            if door.is_active:
                any_door_active = True

        # Show/hide interaction prompt based on door proximity
        if any_door_active:
            self.ui_manager.show_interaction_prompt()
        else:
            try:
                self.ui_manager.hide_interaction_prompt()
            except KeyError:
                pass  # Ignore if prompt was already hidden

        # Update UI elements
        self.ui_manager.update(dt, self.player.position, view_matrix)

        # Update remaining entities
        for entity_type, entities in self.entities.items():
            if entity_type != ENTITY_TYPE["DOOR"]:  # Doors already updated
                for entity in entities:
                    entity.update(dt, self.player.position)
        
        # Update lights
        for light in self.lights:
            light.update(dt, self.player.position)

    def move_player(self, d_pos: list[float]) -> None:
        """
            move the player by the given amount in the 
            (forwards, right, up) vectors.
        """

        self.player.move(d_pos)
    
    def spin_player(self, d_eulers: list[float]) -> None:
        """
            spin the player by the given amount
            around the (x,y,z) axes
        """

        self.player.spin(d_eulers)

    def get_all_renderables(self) -> dict[int, list[Entity]]:
        """Get all entities that need to be rendered, including UI elements"""
        renderables = self.entities.copy()
        
        # Add UI elements to renderables
        ui_elements = self.ui_manager.get_renderable_elements()
        for entity_type, elements in ui_elements.items():
            if entity_type not in renderables:
                renderables[entity_type] = []
            renderables[entity_type].extend(elements)
        
        return renderables
