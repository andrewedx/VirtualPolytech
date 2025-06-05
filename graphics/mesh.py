from OpenGL.GL import *
import numpy as np
from utils.obj_loader import *
from graphics.material import *



class Mesh:
    """
        A basic mesh which can hold data and be drawn.
    """
    __slots__ = ("vao", "vbo", "vertex_count")


    def __init__(self):
        """
            Initialize the mesh.
        """

        # x, y, z, s, t, nx, ny, nz
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def arm_for_drawing(self) -> None:
        """
            Arm the triangle for drawing.
        """
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """
            Draw the triangle.
        """

        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class ObjMesh(Mesh):
    """
        A mesh which is initialized from an obj file.
    """
    __slots__ = ("texture_path",)


    def __init__(self, filename: str):
        """
            Initialize the mesh.
        """
        print(f"Loading mesh from {filename}")
        super().__init__()
        print("init done")

        # x, y, z, s, t, nx, ny, nz
        vertices, texture_path = load_mesh(filename)
        print("texturepath= ", texture_path)
        self.texture_path = texture_path or "gfx/wood.jpg"
        self.vertex_count = len(vertices)//8 
        vertices = np.array(vertices, dtype=np.float32)

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

class RectMesh(Mesh):
    """
        A mesh which constructs its vertices to represent
        a rectangle.
    """
    __slots__ = tuple()


    def __init__(self, w: float, h: float):
        """
            Initialize the rectangle mesh to the given
            width and height.
        """

        super().__init__()

        vertices = (
            0, -w/2,  h/2, 0, 0, 1, 0, 0,
            0, -w/2, -h/2, 0, 1, 1, 0, 0,
            0,  w/2, -h/2, 1, 1, 1, 0, 0,

            0, -w/2,  h/2, 0, 0, 1, 0, 0,
            0,  w/2, -h/2, 1, 1, 1, 0, 0,
            0,  w/2,  h/2, 1, 0, 1, 0, 0
        )
        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = 6
        
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

class MultiMaterialMesh:
    def __init__(self, filename: str):
        self.submeshes = []  # list of dicts with vao, vbo, vertex_count, texture

        

        groups = load_multi_material_mesh(filename)

        for mat_name, data in groups.items():
            vao = glGenVertexArrays(1)
            vbo = glGenBuffers(1)

            glBindVertexArray(vao)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

            vertices = np.array(data["vertices"], dtype=np.float32)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

            texture_path = data.get("texture")
            color = data.get("color", [1.0, 1.0, 1.0])
            print("texture_path= ", texture_path)
            print("color= ", color)

            if texture_path:
                material = Material(texture_path)
            else:
                material = ColorMaterial(color)

            self.submeshes.append({
                "vao": vao,
                "vbo": vbo,
                "count": len(vertices) // 8,
                "material": material
            })

    def render(self):
        for sub in self.submeshes:
            sub["material"].use()
            glBindVertexArray(sub["vao"])
            glDrawArrays(GL_TRIANGLES, 0, sub["count"])

    def destroy(self):
        for sub in self.submeshes:
            glDeleteVertexArrays(1, (sub["vao"],))
            glDeleteBuffers(1, (sub["vbo"],))
            sub["material"].destroy()

class SkyboxMesh(Mesh):
    def __init__(self):
        super().__init__()
        vertices = np.array([
            -1,  1, -1,  -1, -1, -1,   1, -1, -1,
             1, -1, -1,   1,  1, -1,  -1,  1, -1,  # back
            -1, -1,  1,  -1, -1, -1,  -1,  1, -1,
            -1,  1, -1,  -1,  1,  1,  -1, -1,  1,  # left
             1, -1, -1,   1, -1,  1,   1,  1,  1,
             1,  1,  1,   1,  1, -1,   1, -1, -1,  # right
            -1, -1,  1,  -1,  1,  1,   1,  1,  1,
             1,  1,  1,   1, -1,  1,  -1, -1,  1,  # front
            -1,  1, -1,   1,  1, -1,   1,  1,  1,
             1,  1,  1,  -1,  1,  1,  -1,  1, -1,  # top
            -1, -1, -1,  -1, -1,  1,   1, -1,  1,
             1, -1,  1,   1, -1, -1,  -1, -1, -1   # bottom
        ], dtype=np.float32)

        self.vertex_count = len(vertices) // 3

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
