from OpenGL.GL import *
import numpy as np
import pyrr

from core.constants import *
from graphics.shader import Shader
from graphics.mesh import *
from graphics.material import Material
from graphics.skybox import Skybox
from core.scene import Camera
from entities.pointlight import PointLight
from entities.base import Entity
from utils.colors import *

class GraphicsEngine:
    """
        Draws entities and stuff.
    """
    __slots__ = ("meshes", "materials", "shaders", "skybox_mesh", "skybox_shader", "skybox", "shadow_fbo", "shadow_depth_texture", "shadow_width", "shadow_height", "shadows_enabled", "window_width", "window_height")

    def __init__(self):
        """
            Initializes the rendering system.
        """

        self.window_width = SCREEN_WIDTH
        self.window_height = SCREEN_HEIGHT

        self._set_up_opengl()

        self._create_assets()

        self._set_onetime_uniforms()

        self._get_uniform_locations()

        self._create_shadow_map()

        self.shadows_enabled = True

        ## set up skybox
        self.skybox_mesh = SkyboxMesh()
        self.skybox_shader = Shader("shaders/skybox_vertex.txt", "shaders/skybox_fragment.txt")
        self.skybox = Skybox([
            "gfx/texture.png",
            "gfx/texture.png",
            "gfx/texture.png",
            "gfx/texture.png",
            "gfx/texture.png",
            "gfx/texture.png"
        ])
    
    def _set_up_opengl(self) -> None:
        """
            Configure any desired OpenGL options
        """
        r,g,b = hex_to_rgb("#028058")
        print(r,g,b)
        glClearColor(r, g, b, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)

    def _create_assets(self) -> None:
        """
            Create all of the assets needed for drawing.
        """

        # monkey_model = ObjMesh("models/monkeyTextured.obj")
        

        self.meshes: dict[int, Mesh] = {
            # ENTITY_TYPE["CUBE"]: monkey_model,
            ENTITY_TYPE["MEDKIT"]: RectMesh(w = 0.6, h = 0.5),
            ENTITY_TYPE["POINTLIGHT"]: RectMesh(w = 0.2, h = 0.1),
            ENTITY_TYPE["CUBE"] : MultiMaterialMesh("models/joint.obj"),
            ENTITY_TYPE["DOOR"]: MultiMaterialMesh("models/door.obj")
            
        }


        self.materials: dict[int, Material] = {
            # ENTITY_TYPE["CUBE"]: Material(monkey_model.texture_path),
            ENTITY_TYPE["MEDKIT"]: Material("gfx/medkit.png"),
            ENTITY_TYPE["POINTLIGHT"]: Material("gfx/Light-bulb.png"),
            ENTITY_TYPE["PROMPT"]: Material("gfx/medkit.png")  # Still using medkit texture temporarily
        }
        
        self.shaders: dict[int, Shader] = {
            PIPELINE_TYPE["STANDARD"]: Shader(
                "shaders/vertex.txt", "shaders/fragment.txt"),
            PIPELINE_TYPE["EMISSIVE"]: Shader(
                "shaders/vertex_light.txt", "shaders/fragment_light.txt"),
            PIPELINE_TYPE["SHADOW"]: Shader(
                "shaders/shadow_vertex.txt", "shaders/shadow_fragment.txt")
        }
    
    def _set_onetime_uniforms(self) -> None:
        """
            Some shader data only needs to be set once.
        """

        ratio = self.window_width / self.window_height
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=ratio, near=0.1, far=1000, dtype=np.float32
        )

        for shader in self.shaders.values():
            shader.use()
            glUniform1i(glGetUniformLocation(shader.program, "imageTexture"), 0)

            glUniformMatrix4fv(
                glGetUniformLocation(shader.program,"projection"),
                1, GL_FALSE, projection_transform
            )

    def _get_uniform_locations(self) -> None:
        """
            Query and store the locations of shader uniforms
        """

        shader = self.shaders[PIPELINE_TYPE["STANDARD"]]
        shader.use()

        shader.cache_single_location(
            UNIFORM_TYPE["CAMERA_POS"], "cameraPosition")
        shader.cache_single_location(UNIFORM_TYPE["MODEL"], "model")
        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")

        for i in range(MAX_LIGHTS):
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_COLOR"], f"Lights[{i}].color")
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_POS"], f"Lights[{i}].position")
            shader.cache_multi_location(
                UNIFORM_TYPE["LIGHT_STRENGTH"], f"Lights[{i}].strength")
        
        shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["MODEL"], "model")
        shader.cache_single_location(UNIFORM_TYPE["VIEW"], "view")
        shader.cache_single_location(UNIFORM_TYPE["TINT"], "tint")

        shader = self.shaders[PIPELINE_TYPE["SHADOW"]]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["MODEL"], "model")
        shader.cache_single_location(UNIFORM_TYPE["LIGHT_MATRIX"], "lightSpaceMatrix")


    
    def _create_shadow_map(self) -> None:
        """
            Create a framebuffer and texture to render shadows into.
        """

        self.shadow_width = 1024
        self.shadow_height = 1024

        self.shadow_fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.shadow_fbo)

        self.shadow_depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.shadow_depth_texture)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
            self.shadow_width, self.shadow_height,
            0, GL_DEPTH_COMPONENT, GL_FLOAT, None
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1.0, 1.0, 1.0, 1.0])

        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
            GL_TEXTURE_2D, self.shadow_depth_texture, 0
        )
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Error: Framebuffer is not complete!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def _get_light_space_matrix(self, light_pos: np.ndarray) -> np.ndarray:
        """
            Calculate the light-space transformation matrix.

            Parameters:
                light_pos: position of the light source

            Returns:
                light space matrix
        """

        # Use a larger projection range to ensure it covers the entire scene
        light_projection = pyrr.matrix44.create_orthogonal_projection(
            left=-30, right=30,
            bottom=-30, top=30,
            near=-30, far=50,
            dtype=np.float32
        )

        # Look from light position towards scene center
        light_view = pyrr.matrix44.create_look_at(
            eye=light_pos,
            target=np.array([0, 0, 0], dtype=np.float32),  # Look at scene center
            up=np.array([0, 1, 0], dtype=np.float32),      # World up vector
            dtype=np.float32
        )

        return pyrr.matrix44.multiply(light_projection, light_view)
    
    def _update_projection_matrices(self) -> None:
        aspect = self.window_width / self.window_height
        projection = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=aspect, near=0.1, far=1000, dtype=np.float32
        )
        for shader in self.shaders.values():
            shader.use()
            loc = glGetUniformLocation(shader.program, "projection")
            if loc != -1:  # Only update if the shader uses this uniform
                glUniformMatrix4fv(loc, 1, GL_FALSE, projection)



    def _recreate_shadow_map(self, width: int, height: int) -> None:
        # Delete old framebuffer and texture
        glDeleteFramebuffers(1, [self.shadow_fbo])
        glDeleteTextures(1, [self.shadow_depth_texture])

        self.shadow_width = width
        self.shadow_height = height

        # Generate framebuffer
        self.shadow_fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.shadow_fbo)

        # Generate depth texture
        self.shadow_depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.shadow_depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
                    self.shadow_width, self.shadow_height, 0,
                    GL_DEPTH_COMPONENT, GL_FLOAT, None)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)

        border_color = [1.0, 1.0, 1.0, 1.0]
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border_color)

        # Attach depth texture to framebuffer
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                            GL_TEXTURE_2D, self.shadow_depth_texture, 0)

        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)

        # Unbind framebuffer
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def resize(self, width: int, height: int) -> None:
        self.window_width = width
        self.window_height = height
        self._update_projection_matrices()
        self._recreate_shadow_map(width, height)
    
    def render(self, camera: Camera, renderables: dict[int, list[Entity]], lights: list[PointLight]) -> None:
        """
            Render a frame.

            Parameters:
                camera: the scene's camera
                renderables: dictionary mapping entity types to lists of entities
                lights: all the lights in the scene
        """
        # Get all renderables including UI elements
        all_renderables = renderables.get_all_renderables() if hasattr(renderables, 'get_all_renderables') else renderables

        # Sort lights by distance to camera and take only the closest MAX_LIGHTS
        sorted_lights = sorted(
            lights,
            key=lambda light: np.linalg.norm(light.position - camera.position)
        )[:MAX_LIGHTS]
        
        # Fill remaining slots with dummy lights (strength = 0)
        while len(sorted_lights) < MAX_LIGHTS:
            sorted_lights.append(PointLight(
                position=[0, 0, 0],
                color=[0, 0, 0],
                strength=0
            ))

        light_space_matrix = np.identity(4, dtype=np.float32)

        if self.shadows_enabled and len(lights) > 0:
            # STEP 1: Render shadow map
            glViewport(0, 0, self.shadow_width, self.shadow_height)
            glBindFramebuffer(GL_FRAMEBUFFER, self.shadow_fbo)
            glClear(GL_DEPTH_BUFFER_BIT)

            shadow_shader = self.shaders[PIPELINE_TYPE["SHADOW"]]
            shadow_shader.use()

            light_pos = sorted_lights[0].position  # Use the closest light for shadows
            light_space_matrix = self._get_light_space_matrix(light_pos)

            glUniformMatrix4fv(
                shadow_shader.fetch_single_location(UNIFORM_TYPE["LIGHT_MATRIX"]),
                1, GL_FALSE, light_space_matrix
            )

            for entity_type, entities in all_renderables.items():
                if entity_type == ENTITY_TYPE["MEDKIT"]:  # Skip UI elements for shadow pass
                    continue
                mesh = self.meshes[entity_type]
                if isinstance(mesh, MultiMaterialMesh):
                    for entity in entities:
                        glUniformMatrix4fv(
                            shadow_shader.fetch_single_location(UNIFORM_TYPE["MODEL"]),
                            1, GL_FALSE, entity.get_model_transform()
                        )
                        mesh.render()
                else:
                    mesh.arm_for_drawing()
                    for entity in entities:
                        glUniformMatrix4fv(
                            shadow_shader.fetch_single_location(UNIFORM_TYPE["MODEL"]),
                            1, GL_FALSE, entity.get_model_transform()
                        )
                        mesh.draw()

            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, self.window_width, self.window_height)

        # STEP 2: Main geometry render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        view = camera.get_view_transform()
        
        # First render standard objects
        shader = self.shaders[PIPELINE_TYPE["STANDARD"]]
        shader.use()
        glUniform1i(glGetUniformLocation(shader.program, "shadowsEnabled"), int(self.shadows_enabled and len(lights) > 0))

        # Pass light-space matrix and shadow map
        glUniformMatrix4fv(
            glGetUniformLocation(shader.program, "lightSpaceMatrix"),
            1, GL_FALSE, light_space_matrix
        )

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.shadow_depth_texture)
        glUniform1i(glGetUniformLocation(shader.program, "shadowMap"), 1)

        glUniformMatrix4fv(
            shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
            1, GL_FALSE, view
        )
        glUniform3fv(
            shader.fetch_single_location(UNIFORM_TYPE["CAMERA_POS"]),
            1, camera.position
        )

        # Send only the closest lights to shader
        for i, light in enumerate(sorted_lights):
            glUniform3fv(shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_POS"], i), 1, light.position)
            glUniform3fv(shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_COLOR"], i), 1, light.color)
            glUniform1f(shader.fetch_multi_location(UNIFORM_TYPE["LIGHT_STRENGTH"], i), light.strength)

        # Render non-UI elements with standard shader
        for entity_type, entities in all_renderables.items():
            if entity_type == ENTITY_TYPE["MEDKIT"]:  # Skip UI elements for now
                continue
                
            mesh = self.meshes[entity_type]
            if isinstance(mesh, MultiMaterialMesh):
                for entity in entities:
                    glUniformMatrix4fv(
                        shader.fetch_single_location(UNIFORM_TYPE["MODEL"]),
                        1, GL_FALSE, entity.get_model_transform()
                    )
                    mesh.render()
            else:
                if entity_type not in self.materials:
                    continue
                self.materials[entity_type].use()
                mesh.arm_for_drawing()
                for entity in entities:
                    glUniformMatrix4fv(
                        shader.fetch_single_location(UNIFORM_TYPE["MODEL"]),
                        1, GL_FALSE, entity.get_model_transform()
                    )
                    mesh.draw()

        # Draw emissive objects (e.g., point lights)
        emissive_shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
        emissive_shader.use()
        glUniformMatrix4fv(
            emissive_shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
            1, GL_FALSE, view
        )

        material = self.materials[ENTITY_TYPE["POINTLIGHT"]]
        mesh = self.meshes[ENTITY_TYPE["POINTLIGHT"]]
        material.use()
        mesh.arm_for_drawing()
        for light in sorted_lights:
            glUniform3fv(
                emissive_shader.fetch_single_location(UNIFORM_TYPE["TINT"]), 
                1, light.color
            )
            glUniformMatrix4fv(
                emissive_shader.fetch_single_location(UNIFORM_TYPE["MODEL"]),
                1, GL_FALSE, light.get_model_transform()
            )
            mesh.draw()

        # Draw skybox
        glDepthFunc(GL_LEQUAL)
        self.skybox_shader.use()

        skybox_view = pyrr.matrix44.create_from_matrix33(
            pyrr.matrix33.create_from_matrix44(view)
        )
        aspect = self.window_width / self.window_height
        projection = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=aspect, near=0.1, far=1000
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.skybox_shader.program, "view"),
            1, GL_FALSE, skybox_view
        )
        glUniformMatrix4fv(
            glGetUniformLocation(self.skybox_shader.program, "projection"),
            1, GL_FALSE, projection
        )

        self.skybox.use()
        self.skybox_mesh.arm_for_drawing()
        self.skybox_mesh.draw()
        glDepthFunc(GL_LESS)

        # Now render UI elements with emissive shader (as the very last step)
        if ENTITY_TYPE["MEDKIT"] in all_renderables:
            emissive_shader = self.shaders[PIPELINE_TYPE["EMISSIVE"]]
            emissive_shader.use()
            glUniformMatrix4fv(
                emissive_shader.fetch_single_location(UNIFORM_TYPE["VIEW"]),
                1, GL_FALSE, view
            )

            prompt_material = self.materials[ENTITY_TYPE["MEDKIT"]]
            prompt_mesh = self.meshes[ENTITY_TYPE["MEDKIT"]]

            prompt_material.use()
            prompt_mesh.arm_for_drawing()

            # Disable depth testing for UI elements
            glDisable(GL_DEPTH_TEST)

            # Render all UI elements
            for entity in all_renderables[ENTITY_TYPE["MEDKIT"]]:
                # Make UI elements glow white
                glUniform3fv(
                    emissive_shader.fetch_single_location(UNIFORM_TYPE["TINT"]), 
                    1, np.array([1.0, 1.0, 1.0], dtype=np.float32)
                )
                glUniformMatrix4fv(
                    emissive_shader.fetch_single_location(UNIFORM_TYPE["MODEL"]),
                    1, GL_FALSE,
                    entity.get_model_transform()
                )
                prompt_mesh.draw()

            # Re-enable depth testing for other objects
            glEnable(GL_DEPTH_TEST)

        glFlush()

    def toggle_shadows(self):
        self.shadows_enabled = not self.shadows_enabled
        print("Shadows enabled:", self.shadows_enabled)

    def reload_shaders(self):
        print("Reloading shaders...")

        # Destroy old programs
        for shader in self.shaders.values():
            shader.destroy()

        # Rebuild everything
        self._create_assets()
        self._get_uniform_locations()
        self._set_onetime_uniforms()


    def destroy(self) -> None:
        """ free any allocated memory """

        for mesh in self.meshes.values():
            mesh.destroy()
        for material in self.materials.values():
            material.destroy()
        for shader in self.shaders.values():
            shader.destroy()

        glDeleteFramebuffers(1, [self.shadow_fbo])
        glDeleteTextures(1, [self.shadow_depth_texture])
        self.skybox.destroy()
        self.skybox_mesh.destroy()
        self.skybox_shader.destroy()
