def hex_to_rgb(hex_color):
    """
    Convert a hex color string to an RGB tuple.
    
    Args:
        hex_color (str): A hex color string, e.g., '#FF5733'.
    
    Returns:
        tuple: A tuple representing the RGB values, e.g., (255, 87, 51).
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16)/255.0 for i in (0, 2, 4))