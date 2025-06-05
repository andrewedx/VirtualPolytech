from OpenGL.GL import *
from PIL import Image

class Skybox:
    def __init__(self, faces: list[str]):
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id)

        for i, face in enumerate(faces):
            with Image.open(face) as img:
                img = img.convert("RGB")
                img_data = img.tobytes()
                width, height = img.size
                glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB,
                             width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    def use(self):
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id)

    def destroy(self):
        glDeleteTextures(1, [self.texture_id])
