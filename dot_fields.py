"""
Dot Fields - Cellular Automata Simulation

This module implements a cellular automata simulation where pixels change
color based on their neighbors and random chance.

Color progression: Black -> Red -> Orange -> Yellow -> Green -> Blue -> Purple
"""

import random
from typing import List, Tuple

# Color definitions
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

COLORS = [BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]


class DotField:
    """A 2D grid of pixels that evolves through cellular automata."""

    def __init__(self, width: int = 512, height: int = 512):
        """Initialize a grid of black pixels."""
        self.width = width
        self.height = height
        self.grid: List[List[int]] = [
            [0 for _ in range(width)] for _ in range(height)
        ]  # 0 = BLACK, 1 = RED, etc.

    def get_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get the RGB color at position (x, y)."""
        color_index = self.grid[y][x]
        return COLORS[color_index]

    def set_color(self, x: int, y: int, color_index: int):
        """Set the color at position (x, y) to the given color index."""
        self.grid[y][x] = color_index

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get the 8 neighboring positions for a pixel."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def get_color_index(self, x: int, y: int) -> int:
        """Get the color index at position (x, y)."""
        return self.grid[y][x]

    def has_neighbor_of_color(self, x: int, y: int, color_index: int) -> bool:
        """Check if any neighbor has the specified color index."""
        for nx, ny in self.get_neighbors(x, y):
            if self.get_color_index(nx, ny) == color_index:
                return True
        return False

    def generation(self):
        """Advance one generation of the cellular automata."""
        # Create a copy of the grid to store next state
        new_grid = [row[:] for row in self.grid]

        for y in range(self.height):
            for x in range(self.width):
                current_color = self.get_color_index(x, y)

                if current_color == 0:  # BLACK
                    # 1 in 100 chance of turning red
                    if random.randint(1, 100) == 1:
                        new_grid[y][x] = 1  # RED
                elif 1 <= current_color <= 5:  # RED through BLUE
                    # If adjacent to same color, advance to next color
                    if self.has_neighbor_of_color(x, y, current_color):
                        new_grid[y][x] = current_color + 1

        self.grid = new_grid

    def has_purple(self) -> bool:
        """Check if there is at least one purple pixel."""
        for y in range(self.height):
            for x in range(self.width):
                if self.get_color_index(x, y) == 6:  # PURPLE
                    return True
        return False

    def count_color(self, color_index: int) -> int:
        """Count the number of pixels with the given color index."""
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.get_color_index(x, y) == color_index:
                    count += 1
        return count

    def save_png(self, filename: str):
        """Save the grid as a PNG file."""
        # PNG header
        header = b'\x89PNG\r\n\x1a\n'
        
        # IHDR chunk
        ihdr_data = (
            self.width.to_bytes(4, 'big') +
            self.height.to_bytes(4, 'big') +
            b'\x08\x02' +  # 8-bit RGBA
            b'\x00\x00\x00'  # no compression, no filters, no interlace
        )
        ihdr_crc = self._crc32(b'IHDR' + ihdr_data)
        ihdr_chunk = len(ihdr_data).to_bytes(4, 'big') + b'IHDR' + ihdr_data + ihdr_crc.to_bytes(4, 'big')
        
        # IDAT chunk (image data)
        raw_data = b''
        for y in range(self.height):
            raw_data += b'\x00'  # filter type 0 (none)
            for x in range(self.width):
                color = self.get_color(x, y)
                raw_data += bytes(color) + b'\xff'  # RGB + alpha
        
        idat_data = raw_data
        idat_crc = self._crc32(b'IDAT' + idat_data)
        idat_chunk = len(idat_data).to_bytes(4, 'big') + b'IDAT' + idat_data + idat_crc.to_bytes(4, 'big')
        
        # IEND chunk
        iend_crc = self._crc32(b'IEND')
        iend_chunk = b'\x00\x00\x00\x00IEND\xae\x42\x60\x82'
        
        # Write file
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(ihdr_chunk)
            f.write(idat_chunk)
            f.write(iend_chunk)

    def _crc32(self, data: bytes) -> int:
        """Compute CRC32 checksum."""
        crc = 0xFFFFFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xEDB88320
                else:
                    crc >>= 1
        return crc ^ 0xFFFFFFFF


def run_simulation():
    """Run the dot fields simulation until at least one purple pixel appears."""
    dot_field = DotField(512, 512)
    generation = 0
    
    while not dot_field.has_purple():
        dot_field.generation()
        generation += 1
        
        # Print progress every 100 generations
        if generation % 100 == 0:
            red_count = dot_field.count_color(1)
            orange_count = dot_field.count_color(2)
            yellow_count = dot_field.count_color(3)
            green_count = dot_field.count_color(4)
            blue_count = dot_field.count_color(5)
            purple_count = dot_field.count_color(6)
            print(f"Generation {generation}: "
                  f"Red={red_count}, Orange={orange_count}, Yellow={yellow_count}, "
                  f"Green={green_count}, Blue={blue_count}, Purple={purple_count}")
    
    print(f"\nSimulation complete after {generation} generations.")
    print(f"Generating purple.png...")
    dot_field.save_png('purple.png')
    print(f"Image saved to purple.png")
    
    return generation


if __name__ == '__main__':
    run_simulation()
