import random


class DotField:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        # Initialize with all black pixels
        self.pixels = [[0 for _ in range(width)] for _ in range(height)]

    def get(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return None

    def set(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def get_neighbors(self, x, y):
        """Get all 8 neighboring pixels."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors

    def has_neighbor_of_color(self, x, y, color):
        """Check if any neighbor has the specified color."""
        for nx, ny in self.get_neighbors(x, y):
            if self.get(nx, ny) == color:
                return True
        return False

    def generation(self):
        """Run one generation of the cellular automata."""
        # Create a copy of current pixels to update
        new_pixels = [[self.pixels[y][x] for x in range(self.width)] for y in range(self.height)]

        # Process each pixel
        for y in range(self.height):
            for x in range(self.width):
                current = self.pixels[y][x]

                # Black pixel has 1% chance to turn red
                if current == 0:
                    if random.randint(1, 100) == 1:
                        new_pixels[y][x] = 1  # Red

                # Color progression with neighbor check
                elif current == 1:  # Red
                    if self.has_neighbor_of_color(x, y, 2):  # Orange neighbor
                        new_pixels[y][x] = 2  # Orange
                elif current == 2:  # Orange
                    if self.has_neighbor_of_color(x, y, 3):  # Yellow neighbor
                        new_pixels[y][x] = 3  # Yellow
                elif current == 3:  # Yellow
                    if self.has_neighbor_of_color(x, y, 4):  # Green neighbor
                        new_pixels[y][x] = 4  # Green
                elif current == 4:  # Green
                    if self.has_neighbor_of_color(x, y, 5):  # Blue neighbor
                        new_pixels[y][x] = 5  # Blue
                elif current == 5:  # Blue
                    if self.has_neighbor_of_color(x, y, 6):  # Purple neighbor
                        new_pixels[y][x] = 6  # Purple

        self.pixels = new_pixels

    def has_purple(self):
        """Check if there is at least one purple pixel."""
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] == 6:  # Purple
                    return True
        return False

    def count_color(self, color):
        """Count pixels of a specific color."""
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] == color:
                    count += 1
        return count

    def to_png(self, filename):
        """Write the grid to a PNG file."""
        # Color palette: black, red, orange, yellow, green, blue, purple
        palette = [
            (0, 0, 0),         # Black
            (255, 0, 0),       # Red
            (255, 165, 0),     # Orange
            (255, 255, 0),     # Yellow
            (0, 255, 0),       # Green
            (0, 0, 255),       # Blue
            (128, 0, 128),     # Purple
        ]

        with open(filename, 'wb') as f:
            # PNG signature
            f.write(b'\x89PNG\r\n\x1a\n')

            # IHDR chunk
            width = self.width
            height = self.height
            ihdr_data = (
                width.to_bytes(4, 'big') +
                height.to_bytes(4, 'big') +
                b'\x08\x02' +  # 8-bit RGB
                b'\x00' +     # No compression
                b'\x00' +     # No filter
                b'\x00'       # No interlace
            )
            f.write((len(ihdr_data) + 4).to_bytes(4, 'big'))  # Length
            f.write(b'IHDR')
            f.write(ihdr_data)
            self._write_crc(f, b'IHDR', ihdr_data)

            # IDAT chunk (compressed image data)
            raw_data = b''
            for y in range(height):
                raw_data += b'\x00'  # Filter type: none
                for x in range(width):
                    color_index = self.pixels[y][x]
                    f.write(bytes(palette[color_index]))

            # Write IDAT with compression
            import zlib
            compressed = zlib.compress(raw_data)
            f.write((len(compressed) + 4).to_bytes(4, 'big'))  # Length
            f.write(b'IDAT')
            f.write(compressed)
            self._write_crc(f, b'IDAT', compressed)

            # IEND chunk
            f.write((0).to_bytes(4, 'big'))  # Length
            f.write(b'IEND')
            self._write_crc(f, b'IEND', b'')

    def _write_crc(self, f, chunk_type, data):
        """Write CRC for a PNG chunk."""
        import struct
        import binascii
        crc = binascii.crc32(chunk_type + data) & 0xffffffff
        f.write(crc.to_bytes(4, 'big'))


def run_simulation():
    """Run the dot field simulation until a purple pixel appears."""
    dot_field = DotField(512, 512)
    generation_count = 0

    while not dot_field.has_purple():
        dot_field.generation()
        generation_count += 1
        if generation_count % 100 == 0:
            print(f"Generation {generation_count}: {dot_field.count_color(6)} purple pixels")

    print(f"Simulation completed in {generation_count} generations")
    print(f"Final purple pixel count: {dot_field.count_color(6)}")

    dot_field.to_png("purple.png")
    print("Output saved to purple.png")

    return generation_count


if __name__ == "__main__":
    run_simulation()
