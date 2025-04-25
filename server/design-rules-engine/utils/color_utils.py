import re
from typing import Tuple, Union

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def get_luminance(color: Union[str, Tuple[int, int, int]]) -> float:
    """Calculate relative luminance of a color."""
    if isinstance(color, str):
        rgb = hex_to_rgb(color)
    else:
        rgb = color
    
    # Convert to sRGB
    r, g, b = [x / 255.0 for x in rgb]
    
    # Apply gamma correction
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    
    # Calculate luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two colors."""
    l1 = get_luminance(color1)
    l2 = get_luminance(color2)
    
    lighter = max(l1, l2)
    darker = min(l1, l2)
    
    return (lighter + 0.05) / (darker + 0.05)

def is_color_accessible(text_color: str, background_color: str, 
                       is_large_text: bool = False) -> bool:
    """Check if color combination meets WCAG standards."""
    contrast_ratio = calculate_contrast_ratio(text_color, background_color)
    min_ratio = 3.0 if is_large_text else 4.5
    return contrast_ratio >= min_ratio

def parse_color(color_string: str) -> Tuple[int, int, int]:
    """Parse various color formats to RGB."""
    # Hex format
    if color_string.startswith('#'):
        return hex_to_rgb(color_string)
    
    # RGB format
    rgb_match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_string)
    if rgb_match:
        return tuple(map(int, rgb_match.groups()))
    
    # RGBA format
    rgba_match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)', color_string)
    if rgba_match:
        return tuple(map(int, rgba_match.groups()))
    
    # Named colors (simplified)
    named_colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        # Add more as needed
    }
    
    return named_colors.get(color_string.lower(), (0, 0, 0))