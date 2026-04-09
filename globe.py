#!/usr/bin/env python3
"""
Iconic Number Sphere - A rotating 3D ASCII globe made of digits 0-9
Run with: python globe.py
No pip installs required - uses only standard library
"""

import math
import time
import os
import sys

def create_sphere(size=20, rotation=0):
    """
    Create a 3D rotating sphere made of digits 0-9.
    Projects sphere onto 2D terminal display.
    """
    width = size * 2
    height = size
    
    # Create output grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Precompute rotation matrix values
    cos_rot = math.cos(rotation)
    sin_rot = math.sin(rotation)
    
    # Continental data - simplified landmass representation (lat, lon, weight)
    continents = [
        # North America
        (45, -100, 0.8), (40, -90, 0.9), (35, -100, 0.7),
        # South America
        (0, -60, 0.8), (-15, -60, 0.9), (-30, -60, 0.7),
        # Africa
        (0, 20, 0.85), (10, 30, 0.9), (-10, 30, 0.8),
        # Europe
        (50, 15, 0.8), (55, 25, 0.85),
        # Asia
        (50, 100, 0.9), (40, 90, 0.85), (30, 120, 0.8),
        # Australia
        (-25, 135, 0.7),
    ]
    
    # Create visibility and character map
    pixels = {}
    
    # Generate sphere
    for y in range(height):
        for x in range(width):
            # Convert screen coordinates to normalized coordinates
            u = (x - width / 2) / (width / 2)
            v = (height / 2 - y) / height
            
            # Check if point is within unit circle (sphere projection)
            r_squared = u * u + v * v
            if r_squared <= 1:
                # Calculate z (depth) using sphere equation: x²+y²+z²=1
                z = math.sqrt(1 - r_squared)
                
                # 3D point before rotation
                x_3d = u
                y_3d = v
                z_3d = z
                
                # Apply rotation around Y axis (vertical)
                x_rot = x_3d * cos_rot - z_3d * sin_rot
                z_rot = x_3d * sin_rot + z_3d * cos_rot
                y_rot = y_3d
                
                # Convert to spherical coordinates for landmass detection
                lat = math.degrees(math.asin(y_rot))
                lon = math.degrees(math.atan2(z_rot, x_rot))
                
                # Determine if this point is land or ocean based on continents
                land_density = 0.2  # Base ocean density
                
                for cont_lat, cont_lon, weight in continents:
                    lat_diff = abs(lat - cont_lat)
                    lon_diff = abs(lon - cont_lon)
                    
                    # Wrap longitude difference
                    if lon_diff > 180:
                        lon_diff = 360 - lon_diff
                    
                    # Distance to continent center
                    dist = math.sqrt(lat_diff * lat_diff + lon_diff * lon_diff)
                    
                    # Gaussian falloff from continent center
                    if dist < 25:
                        continent_effect = weight * math.exp(-(dist ** 2) / 60)
                        land_density = max(land_density, continent_effect)
                
                # Select digit based on depth and land density
                # Closer (higher z) = brighter, land = higher digit
                brightness = int((z_rot + 1) / 2 * 5)  # 0-5 range
                land_factor = int(land_density * 4)  # 0-4 range
                
                digit_index = (brightness + land_factor) % 10
                
                # Store pixel with depth for later rendering
                pixels[(x, y)] = (str(digit_index), z_rot)
    
    # Render pixels with depth sorting
    for (x, y), (char, depth) in sorted(pixels.items(), key=lambda item: item[1][1]):
        if 0 <= y < height and 0 <= x < width:
            grid[y][x] = char
    
    return grid

def clear_screen():
    """Clear terminal screen in a cross-platform way"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_grid(grid, title="Iconic Number Sphere", subtitle="Rotating 3D Digital Globe"):
    """Print the grid to terminal with ANSI color codes"""
    # ANSI color codes
    CYAN = '\033[96m'
    DARK_BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Check if terminal supports color
    try:
        supports_color = sys.stdout.isatty() and os.environ.get('TERM') != 'dumb'
    except:
        supports_color = False
    
    if not supports_color:
        CYAN = DARK_BLUE = RESET = BOLD = ''
    
    # Print header
    print("\n" + CYAN + BOLD + f"{'=' * 60}" + RESET)
    print(CYAN + BOLD + f"{title:^60}" + RESET)
    print(CYAN + BOLD + f"{subtitle:^60}" + RESET)
    print(CYAN + BOLD + f"{'=' * 60}" + RESET + "\n")
    
    # Print grid
    for row in grid:
        line = ''.join(row)
        if supports_color:
            # Color ocean (lower digits) darker, land (higher digits) brighter
            colored_line = ''
            for char in line:
                if char == ' ':
                    colored_line += ' '
                elif int(char) < 4:
                    colored_line += DARK_BLUE + char + RESET
                else:
                    colored_line += CYAN + char + RESET
            print('  ' + colored_line)
        else:
            print('  ' + line)
    
    # Print footer with instructions
    print("\n" + DARK_BLUE + "Press Ctrl+C to stop" + RESET)

def main():
    """Main animation loop"""
    sphere_size = 15
    frame_delay = 0.05  # Animation speed
    rotation_speed = 0.15  # Radians per frame
    
    rotation = 0
    frame = 0
    
    try:
        while True:
            clear_screen()
            
            # Generate and display sphere
            grid = create_sphere(sphere_size, rotation)
            print_grid(grid, 
                      title="⟲ Iconic Number Sphere ⟳",
                      subtitle="Made by International Space University")
            
            # Print frame info
            print(f"\033[94mFrame: {frame} | Rotation: {math.degrees(rotation):.1f}° | Size: {sphere_size*2}x{sphere_size}\033[0m")
            
            # Update rotation
            rotation += rotation_speed
            if rotation >= 2 * math.pi:
                rotation = 0
            
            frame += 1
            time.sleep(frame_delay)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n✓ Sphere visualization ended gracefully.")
        print("Thank you for viewing the Iconic Number Sphere!\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
