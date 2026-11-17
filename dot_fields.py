"""
Dot Fields – a cellular automata simulation of colour dots.

A 512×512 grid of pixels starts black. Each generation:
  - A black pixel has a 1-in-100 chance of turning red.
  - If a red pixel is adjacent (up/down/left/right) to another red pixel it turns orange.
  - An orange pixel adjacent to an orange pixel turns yellow, and so on:
      red → orange → yellow → green → blue → purple.
The simulation runs until at least one purple pixel appears.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Colour constants and progression
# ---------------------------------------------------------------------------

BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

COLORS: List[Tuple[int, int, int]] = [BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]


def color_index(pixel: Tuple[int, int, int]) -> int:
    """Return the index of *pixel* in COLORS.

    Returns 0 (BLACK) when the colour is not yet recognised.
    """
    try:
        return COLORS.index(pixel)
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Grid helpers
# ---------------------------------------------------------------------------

def _neighbors(x: int, y: int, width: int, height: int):
    """Yield (x, y) of the four orthogonal neighbours of (x, y)."""
    if x > 0:
        yield x - 1, y
    if x < width - 1:
        yield x + 1, y
    if y > 0:
        yield x, y - 1
    if y < height - 1:
        yield x, y + 1


# ---------------------------------------------------------------------------
# Simulation class
# ---------------------------------------------------------------------------

class DotField:
    """512×512 grid of pixels that evolves like a cellular automaton."""

    WIDTH = 512
    HEIGHT = 512

    def __init__(self, width: int = WIDTH, height: int = HEIGHT) -> None:
        self.width = width
        self.height = height
        # Initialise every pixel to black.
        self.grid: List[List[Tuple[int, int, int]]] = [
            [BLACK] * width for _ in range(height)
        ]

    def get_pixel(self, x: int, y: int) -> Tuple[int, int, int]:
        return self.grid[y][x]

    def set_pixel(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        self.grid[y][x] = color

    def has_neighbor_of_color(
        self, x: int, y: int, color: Tuple[int, int, int]
    ) -> bool:
        """Return True if any orthogonal neighbour of (x, y) equals *color*."""
        for nx, ny in _neighbors(x, y, self.width, self.height):
            if self.grid[ny][nx] == color:
                return True
        return False

    def generation(self) -> None:
        """Run one generation across the grid (in-place update)."""
        # We build a new grid rather than mutating in-place so that updates
        # within the same generation do not cascade prematurely.
        new_grid = [row[:] for row in self.grid]

        for y in range(self.height):
            for x in range(self.width):
                pixel = self.grid[y][x]
                idx = color_index(pixel)

                # Black pixels have a 1-in-100 chance of turning red.
                if idx == 0 and random.randint(1, 100) == 1:
                    new_grid[y][x] = RED
                    continue

                # Colored pixels advance if they have a same-color neighbour.
                if 0 < idx < len(COLORS):
                    if self.has_neighbor_of_color(x, y, pixel):
                        new_grid[y][x] = COLORS[idx + 1]

        self.grid = new_grid

    def count_purple(self) -> int:
        total = 0
        for row in self.grid:
            for pixel in row:
                if pixel == PURPLE:
                    total += 1
        return total

    def has_purple(self) -> bool:
        for row in self.grid:
            if PURPLE in row:
                return True
        return False

    def run_simulation(self, max_generations: int = 10_000) -> int:
        """Run generations until at least one purple pixel appears.

        Returns the number of generations performed.
        """
        gen = 0
        while not self.has_purple() and gen < max_generations:
            self.generation()
            gen += 1
        return gen

    # ------------------------------------------------------------------
    # PNG output – uses PIL when available, falls back to manual write.
    # ------------------------------------------------------------------

    def save_png(self, path: str | Path) -> None:
        """Save the grid as an RGB PNG file."""
        try:
            from PIL import Image
            width, height = self.width, self.height
            pixels = []
            for y in range(height):
                row = list(self.grid[y])
                pixels.extend(row)
            img = Image.new("RGB", (width, height))
            img.putdata(pixels)
            img.save(path)
        except ImportError:
            # Fallback: write a minimal PNG manually.
            self._save_png_manual(path)

    def _save_png_manual(self, path: str | Path) -> None:
        """Minimal pure-Python PNG writer (used when PIL is unavailable)."""
        import struct, zlib

        width, height = self.width, self.height

        def chunk(chunk_type: bytes, data: bytes) -> bytes:
            c = chunk_type + data
            crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
            return struct.pack(">I", len(data)) + c + crc

        header = b"\x89PNG\r\n\x1a\n"
        ihdr = chunk(
            b"IHDR",
            struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0),
        )
        raw = bytearray()
        for y in range(height):
            raw.append(0)  # filter byte
            for x in range(width):
                r, g, b = self.grid[y][x]
                raw.extend((r, g, b))
        idat = chunk(b"IDAT", zlib.compress(bytes(raw)))
        iend = chunk(b"IEND", b"")

        with open(path, "wb") as f:
            f.write(header + ihdr + idat + iend)


# ---------------------------------------------------------------------------
# Convenience entry-point
# ---------------------------------------------------------------------------

def run_simulation(
    width: int = 512,
    height: int = 512,
    max_generations: int = 10_000,
) -> DotField:
    """Create, simulate, and return a DotField with at least one purple pixel."""
    df = DotField(width=width, height=height)
    df.run_simulation(max_generations=max_generations)
    return df


# ---------------------------------------------------------------------------
# CLI entry-point: python dot_fields.py → saves purple.png
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    df = run_simulation()
    df.save_png("purple.png")
    print(f"Done – {df.count_purple()} purple pixel(s) after simulation.")
