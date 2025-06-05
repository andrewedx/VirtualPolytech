from OpenGL.GL import *
from PIL import Image


class Material:
    """
        A basic texture.
    """
    __slots__ = ("texture",)

    
    def __init__(self, filepath: str):
        """
            Initialize and load the texture.

            Parameters:

                filepath: path to the image file.
        """

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        print(filepath)

        try:
            with open(filepath, mode = "rb"):
                pass
        except FileNotFoundError:
            print(f"Error: Texture file '{filepath}' not found.")
            return
        
        with Image.open(filepath, mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        """
            Arm the texture for drawing.
        """

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)
        glUniform1i(glGetUniformLocation(glGetInteger(GL_CURRENT_PROGRAM), "useTexture"), GL_TRUE)


    def destroy(self) -> None:
        """
            Free the texture.
        """

        glDeleteTextures(1, (self.texture,))

class ColorMaterial:
    def __init__(self, rgb: list[float]):
        self.color = rgb

    def use(self):
        location = glGetUniformLocation(glGetInteger(GL_CURRENT_PROGRAM), "tintColor")
        glUniform3fv(location, 1, self.color)

        use_texture_location = glGetUniformLocation(glGetInteger(GL_CURRENT_PROGRAM), "useTexture")
        glUniform1i(use_texture_location, GL_FALSE)
        glUniform3fv(glGetUniformLocation(glGetInteger(GL_CURRENT_PROGRAM), "tint"), 1, self.color)

    def destroy(self):
        pass
