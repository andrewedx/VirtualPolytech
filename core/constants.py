import numpy as np

############################## Constants ######################################

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

GLOBAL_X = np.array([1,0,0], dtype=np.float32)
GLOBAL_Y = np.array([0,1,0], dtype=np.float32)
GLOBAL_Z = np.array([0,0,1], dtype=np.float32)
WHITE = np.array([1,1,1], dtype=np.float32)

# Maximum number of lights to send to shader
MAX_LIGHTS = 3

ENTITY_TYPE = {
    "CUBE": 0,
    "POINTLIGHT": 1,
    "BILLBOARD": 2,
    "DOOR": 3,
    "PROMPT": 4,
}

UNIFORM_TYPE = {
    "MODEL": 0,
    "VIEW": 1,
    "PROJECTION": 2,
    "CAMERA_POS": 3,
    "LIGHT_COLOR": 4,
    "LIGHT_POS": 5,
    "LIGHT_STRENGTH": 6,
    "TINT": 7,
    "LIGHT_MATRIX": 8,
}

PIPELINE_TYPE = {
    "STANDARD": 0,
    "EMISSIVE": 1,
    "SHADOW": 2,
}