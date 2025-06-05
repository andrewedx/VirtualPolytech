import os
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

############################## helper functions ###############################

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compile and link shader modules to make a shader program.

        Parameters:

            vertex_filepath: path to the text file storing the vertex
                            source code
            
            fragment_filepath: path to the text file storing the
                                fragment source code
        
        Returns:

            A handle to the created shader program
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader


def load_mesh(filename: str) -> tuple[list[float], str | None]:
    """
    Load a mesh from an obj file and try to read the texture path from its .mtl file.

    Returns:
        vertices: list of vertex data
        texture_path: path to texture image (or None if not found)
    """
    v = []
    vt = []
    vn = []
    vertices = []

    mtl_file = None
    material_name = None

    with open(filename, "r") as file:
        for line in file:
            words = line.strip().split()
            if not words:
                continue
            match words[0]:
                case "mtllib":
                    mtl_file = words[1]
                case "usemtl":
                    material_name = words[1]
                case "v":
                    v.append(read_vertex_data(words))
                case "vt":
                    vt.append(read_texcoord_data(words))
                case "vn":
                    vn.append(read_normal_data(words))
                case "f":
                    read_face_data(words, v, vt, vn, vertices)

    texture_path = None
    if mtl_file and material_name:
        texture_path = parse_mtl_for_texture(filename, mtl_file, material_name)

    print("MTL file:", mtl_file)
    print("Material used:", material_name)

    return vertices, texture_path

def read_vertex_data(words: list[str]) -> list[float]:
    """
        Returns a vertex description.
    """

    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]
    
def read_texcoord_data(words: list[str]) -> list[float]:
    """
        Returns a texture coordinate description.
    """

    return [
        float(words[1]),
        float(words[2])
    ]
    
def read_normal_data(words: list[str]) -> list[float]:
    """
        Returns a normal vector description.
    """

    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]

def read_face_data(
    words: list[str], 
    v: list[list[float]], vt: list[list[float]], 
    vn: list[list[float]], vertices: list[float]) -> None:
    """
        Reads an edgetable and makes a face from it.
    """

    triangleCount = len(words) - 3

    for i in range(triangleCount):

        make_corner(words[1], v, vt, vn, vertices)
        make_corner(words[2 + i], v, vt, vn, vertices)
        make_corner(words[3 + i], v, vt, vn, vertices)

def make_corner(corner_description: str, 
    v: list[list[float]], vt: list[list[float]], 
    vn: list[list[float]], vertices: list[float]) -> None:
    """
        Composes a flattened description of a vertex.
    """

    v_vt_vn = corner_description.split("/")
    
    for element in v[int(v_vt_vn[0]) - 1]:
        vertices.append(element)
    for element in vt[int(v_vt_vn[1]) - 1]:
        vertices.append(element)
    for element in vn[int(v_vt_vn[2]) - 1]:
        vertices.append(element)


def parse_mtl_for_texture(obj_file_path: str, mtl_file_name: str, target_material: str) -> str | None:
    """
    Try to parse the .mtl file to find the texture file used by a material.

    Parameters:
        obj_file_path: path to the .obj file
        mtl_file_name: referenced .mtl filename
        target_material: material name to find texture for

    Returns:
        Full path to texture file if found, else None
    """
    mtl_path = os.path.join(os.path.dirname(obj_file_path), mtl_file_name)
    try:
        with open(mtl_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None

    current_material = None
    for line in lines:
        words = line.strip().split()
        if not words:
            continue
        if words[0] == "newmtl":
            current_material = words[1]
        if current_material == target_material and words[0] == "map_Kd":
            return os.path.join(os.path.dirname(obj_file_path), words[1])
        

    return None


def load_multi_material_mesh(obj_file_path: str) -> dict[str, dict]:
    v, vt, vn = [], [], []
    material_groups = {}
    current_material = None
    mtl_file = None

    count = 0

    with open(obj_file_path, "r") as file:
        for line in file:
            words = line.strip().split()
            if not words:
                continue

            match words[0]:
                case "mtllib":
                    mtl_file = words[1]
                case "usemtl":
                    try:
                        current_material = words[1]
                    except IndexError:
                        current_material = "Material.002"
                    if current_material not in material_groups:
                        material_groups[current_material] = {"vertices": []}
                case "v":
                    v.append(read_vertex_data(words))
                case "vt":
                    vt.append(read_texcoord_data(words))
                case "vn":
                    vn.append(read_normal_data(words))
                case "f":
                    if current_material is None:
                        continue
                    face_vertices = []
                    triangleCount = len(words) - 3
                    for i in range(triangleCount):
                        face_vertices += get_corner(words[1], v, vt, vn)
                        face_vertices += get_corner(words[2 + i], v, vt, vn)
                        face_vertices += get_corner(words[3 + i], v, vt, vn)
                    material_groups[current_material]["vertices"].extend(face_vertices)
            count += 1
            if count % 1000 == 0:
                print(f"Processed {count} lines...")

    # Attach texture paths
    if mtl_file:
        mtl_path = os.path.join(os.path.dirname(obj_file_path), mtl_file)
        parse_mtl_for_material_textures(mtl_path, material_groups)

    return material_groups


def get_corner(desc: str, v, vt, vn) -> list[float]:
    v_vt_vn = desc.split("/")

    position = v[int(v_vt_vn[0]) - 1]
    texcoord = [0.0, 0.0]  # default
    normal = [0.0, 0.0, 0.0]  # default

    if len(v_vt_vn) > 1 and v_vt_vn[1]:
        texcoord = vt[int(v_vt_vn[1]) - 1]
    if len(v_vt_vn) > 2 and v_vt_vn[2]:
        normal = vn[int(v_vt_vn[2]) - 1]

    return position + texcoord + normal




def parse_mtl_for_material_textures(mtl_path: str, material_groups: dict):
    try:
        with open(mtl_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return
        

    current_material = None
    for line in lines:
        words = line.strip().split()
        if not words:
            continue
        if words[0] == "newmtl":
            current_material = words[1]
        elif words[0] == "map_Kd" and current_material in material_groups:
            texture_path = os.path.join(os.path.dirname(mtl_path), words[1])
            material_groups[current_material]["texture"] = texture_path.split("\\")[-1]
        elif words[0] == "Kd" and current_material in material_groups:
            rgb = list(map(float, words[1:4]))
            material_groups[current_material]["color"] = rgb
