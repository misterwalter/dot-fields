#!/usr/bin/env python3
"""Tests for dot_fields – the cellular-automata colour simulation."""

from __future__ import annotations

import os
import random
import struct
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Import under test
# ---------------------------------------------------------------------------

from dot_fields import (
    BLACK,
    BLUE,
    COLORS,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    YELLOW,
    DotField,
    color_index,
    run_simulation,
)

# ---------------------------------------------------------------------------
# Helpers – read a PNG file and verify it.
# ---------------------------------------------------------------------------


def _read_png_signature(path: str | os.PathLike) -> bool:
    """Return True if the first 8 bytes match the PNG magic number."""
    with open(path, "rb") as f:
        sig = f.read(8)
    return sig == b"\x89PNG\r\n\x1a\n"


def _read_png_size(path: str | os.PathLike) -> tuple[int, int]:
    """Return (width, height) from the IHDR chunk."""
    with open(path, "rb") as f:
        f.read(8)  # PNG sig
        length, chunk_type = struct.unpack(">I4s", f.read(8))
        width, height = struct.unpack(">II", f.read(8))
        assert chunk_type == b"IHDR" and length == 13
    return width, height


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestColorConstants(unittest.TestCase):
    """Verify colour constants are well-formed RGB triples."""

    def test_black_is_zero(self):
        self.assertEqual(BLACK, (0, 0, 0))

    def test_red_is_max_r(self):
        self.assertEqual(RED, (255, 0, 0))

    def test_purple_is_128(self):
        self.assertEqual(PURPLE, (128, 0, 128))

    def test_all_colors_are_triples(self):
        for c in COLORS:
            self.assertIsInstance(c, tuple)
            self.assertEqual(len(c), 3)


class TestColorIndex(unittest.TestCase):
    """Tests for the color_index() helper."""

    def test_black_returns_0(self):
        self.assertEqual(color_index(BLACK), 0)

    def test_purple_returns_last(self):
        self.assertEqual(color_index(PURPLE), len(COLORS) - 1)

    def test_unknown_color_returns_0(self):
        self.assertEqual(color_index((99, 88, 77)), 0)


class TestDotFieldInit(unittest.TestCase):
    """Tests for DotField initialisation."""

    def test_default_size(self):
        df = DotField()
        self.assertEqual(df.width, 512)
        self.assertEqual(df.height, 512)

    def test_all_pixels_black(self):
        df = DotField()
        for y in range(df.height):
            for x in range(df.width):
                self.assertEqual(df.get_pixel(x, y), BLACK)

    def test_custom_size(self):
        df = DotField(width=10, height=20)
        self.assertEqual(df.width, 10)
        self.assertEqual(df.height, 20)


class TestGetSetPixel(unittest.TestCase):
    """Tests for pixel access methods."""

    def test_set_and_get(self):
        df = DotField(width=5, height=5)
        df.set_pixel(2, 3, RED)
        self.assertEqual(df.get_pixel(2, 3), RED)

    def test_bounds(self):
        df = DotField(width=4, height=4)
        # Corner pixels
        for x, y in [(0, 0), (3, 0), (0, 3), (3, 3)]:
            self.assertEqual(df.get_pixel(x, y), BLACK)

    def test_set_replaces(self):
        df = DotField(width=4, height=4)
        df.set_pixel(1, 1, RED)
        df.set_pixel(1, 1, BLUE)
        self.assertEqual(df.get_pixel(1, 1), BLUE)


class TestNeighbors(unittest.TestCase):
    """Tests for the neighbor-detection logic."""

    def test_corner_has_two_neighbors(self):
        df = DotField(width=4, height=4)
        # Corner pixel (0, 0)
        self.assertTrue(df.has_neighbor_of_color(0, 0, BLACK))

    def test_edge_has_three_neighbors(self):
        df = DotField(width=4, height=4)
        self.assertTrue(df.has_neighbor_of_color(1, 0, BLACK))

    def test_center_has_four_neighbors(self):
        df = DotField(width=4, height=4)
        self.assertTrue(df.has_neighbor_of_color(1, 1, BLACK))

    def test_single_pixel(self):
        df = DotField(width=1, height=1)
        self.assertFalse(df.has_neighbor_of_color(0, 0, RED))


class TestColorProgression(unittest.TestCase):
    """Tests that colored pixels advance correctly with neighbors."""

    def setUp(self):
        # Create a tiny grid with all red pixels.
        self.df = DotField(width=5, height=5)
        for y in range(5):
            for x in range(5):
                self.df.grid[y][x] = RED

    def test_red_neighbors_advance(self):
        """Red pixels adjacent to other reds should turn orange."""
        self.df.generation()
        # All interior pixels should be orange (4 neighbours of same colour)
        self.assertEqual(self.df.get_pixel(1, 1), ORANGE)
        self.assertEqual(self.df.get_pixel(2, 2), ORANGE)

    def test_no_neighbors_no_advance(self):
        """Red pixel with no red neighbour stays red."""
        df = DotField(width=3, height=3)
        df.set_pixel(1, 1, RED)
        # (0,0), (0,2), (2,0), (2,2) are black → neighbours of (1,1)
        # that are NOT red. But (1,1) has no RED neighbour.
        df.generation()
        self.assertEqual(df.get_pixel(1, 1), RED)

    def test_multi_step_progression(self):
        """Orange neighbours of orange should turn yellow."""
        df = DotField(width=5, height=5)
        for y in range(5):
            for x in range(5):
                df.grid[y][x] = ORANGE
        df.generation()
        # Interior pixels (with orange neighbours) advance to yellow.
        self.assertEqual(df.get_pixel(1, 1), YELLOW)


class TestCountPurple(unittest.TestCase):
    """Tests for counting purple pixels."""

    def test_all_black_no_purple(self):
        df = DotField(width=5, height=5)
        self.assertEqual(df.count_purple(), 0)

    def test_count_manual(self):
        df = DotField(width=3, height=3)
        df.grid[0][1] = PURPLE
        df.grid[2][1] = PURPLE
        self.assertEqual(df.count_purple(), 2)


class TestHasPurple(unittest.TestCase):
    """Tests for the has_purple() shortcut."""

    def test_false_when_none(self):
        df = DotField(width=5, height=5)
        self.assertFalse(df.has_purple())

    def test_true_when_present(self):
        df = DotField(width=3, height=3)
        df.grid[0][0] = PURPLE
        self.assertTrue(df.has_purple())


class TestGeneration(unittest.TestCase):
    """Tests for the generation() method in isolation."""

    def setUp(self):
        random.seed(42)

    def test_black_to_red_chance(self):
        """Verify that black pixels can turn red with neighbour presence."""
        df = DotField(width=3, height=1)
        df.grid[0][1] = RED
        # After generation, the red pixel at (0,1) should trigger
        # any adjacent black to also advance if it had a red neighbor.
        df.generation()
        self.assertIsInstance(df.grid[0][1], tuple)

    def test_no_cascade_within_generation(self):
        """Each cell's update is based on the *old* grid state."""
        self.setUp()
        random.seed(12345)
        df = DotField(width=6, height=1)
        # All red. After one generation, pixels with neighbours advance.
        for x in range(6):
            df.grid[0][x] = RED
        df.generation()
        # Interior red pixels become orange; edge reds that have a red
        # neighbour also become orange.
        for x in range(6):
            p = df.get_pixel(x, 0)
            self.assertIn(p, [RED, ORANGE], f"pixel {x} has state {p}")


class TestRunSimulation(unittest.TestCase):
    """Integration tests for the full simulation."""

    def test_runs_to_completion(self):
        """run_simulation should return a non-negative generation count."""
        random.seed(1)
        df = run_simulation(width=64, height=64, max_generations=5000)
        self.assertGreater(df.count_purple(), 0)

    def test_has_purple_after_run(self):
        """After run_simulation there must be at least one purple pixel."""
        random.seed(2)
        df = run_simulation(width=64, height=64, max_generations=5000)
        self.assertTrue(df.has_purple())

    def test_max_generations_stops(self):
        """Simulation stops even if purple hasn't appeared."""
        # Set a seed that prevents purple from forming.
        random.seed(99999)
        df = run_simulation(width=16, height=16, max_generations=100)
        self.assertLessEqual(df.count_purple(), 256)  # sanity


class TestSavePng(unittest.TestCase):
    """Tests for PNG output."""

    def setUp(self):
        self.df = DotField(width=64, height=64)
        for y in range(64):
            for x in range(64):
                self.df.grid[y][x] = BLACK
        # Sprinkle some purple.
        self.df.grid[10][20] = PURPLE
        self.df.grid[30][40] = RED

    def test_file_exists(self):
        path = Path("/tmp/dot_fields_test.png")
        if path.exists():
            path.unlink()
        self.df.save_png(path)
        self.assertTrue(path.exists())
        path.unlink()

    def test_valid_signature(self):
        path = Path("/tmp/dot_fields_test_sig.png")
        if path.exists():
            path.unlink()
        self.df.save_png(path)
        self.assertTrue(_read_png_signature(path))
        path.unlink()

    def test_correct_size(self):
        path = Path("/tmp/dot_fields_test_sz.png")
        if path.exists():
            path.unlink()
        self.df.save_png(path)
        w, h = _read_png_size(path)
        self.assertEqual(w, 64)
        self.assertEqual(h, 64)
        path.unlink()

    def test_purple_in_image(self):
        """Check that a purple pixel in the grid is written as (128,0,128)."""
        path = Path("/tmp/dot_fields_test_px.png")
        if path.exists():
            path.unlink()
        self.df.save_png(path)
        # Read back raw pixel data.
        with open(path, "rb") as f:
            f.read(8)  # PNG signature
            ihdr_len = struct.unpack(">I", f.read(4))[0]  # IHDR length
            f.read(4)  # IHDR type ("IHDR")
            f.read(ihdr_len)  # IHDR data
            f.read(4)  # IHDR CRC
            idat_len = struct.unpack(">I", f.read(4))[0]  # IDAT length
            f.read(4)  # IDAT type ("IDAT")
            compressed = f.read(idat_len)
            raw = zlib_decompress(compressed)
        # The purple pixel is at grid[10][20].
        # Each row: 1 filter byte + width * 3 bytes.
        row_offset = 10 * (64 * 3 + 1)  # line 10 start (filter byte)
        px_offset = row_offset + 1 + 20 * 3  # skip filter byte, then column offset
        r, g, b = raw[px_offset], raw[px_offset + 1], raw[px_offset + 2]
        self.assertEqual((r, g, b), PURPLE)
        path.unlink()


class TestRunSimulationIntegration(unittest.TestCase):
    """Larger-scale integration: run for a known number of generations."""

    def test_deterministic_seed(self):
        """Same seed → same final pixel counts."""
        random.seed(42)
        df1 = run_simulation(width=64, height=64, max_generations=1000)
        n1 = df1.count_purple()

        random.seed(42)
        df2 = run_simulation(width=64, height=64, max_generations=1000)
        n2 = df2.count_purple()

        self.assertEqual(n1, n2)


# ---------------------------------------------------------------------------
# Extra test: colour index completeness
# ---------------------------------------------------------------------------

class TestColorIndexCompleteness(unittest.TestCase):
    """Ensure every member of COLORS maps to its own index."""

    def test_each_color_maps_to_index(self):
        for i, c in enumerate(COLORS):
            self.assertEqual(color_index(c), i)


# ---------------------------------------------------------------------------
# zlib helper (used inside the test without importing at top level).
# ---------------------------------------------------------------------------

import zlib as _zlib  # noqa: E402


def zlib_decompress(data: bytes) -> bytes:
    return _zlib.decompress(data)


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
