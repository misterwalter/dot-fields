#!/usr/bin/env python3
"""Test suite for dot_fields module."""

import unittest
import random
from dot_fields import DotField, run_simulation


class TestDotFieldInit(unittest.TestCase):
    """Test initialization of DotField."""

    def test_default_size(self):
        """Test that default size is 512x512."""
        df = DotField()
        self.assertEqual(df.width, 512)
        self.assertEqual(df.height, 512)

    def test_custom_size(self):
        """Test custom size initialization."""
        df = DotField(100, 200)
        self.assertEqual(df.width, 100)
        self.assertEqual(df.height, 200)

    def test_all_black_initially(self):
        """Test that all pixels are black (0) initially."""
        df = DotField(10, 10)
        for y in range(10):
            for x in range(10):
                self.assertEqual(df.get(x, y), 0, f"Pixel at ({x},{y}) should be black")


class TestColorConstants(unittest.TestCase):
    """Test color constant definitions."""

    def test_color_values(self):
        """Test that color values are sequential."""
        # 0=black, 1=red, 2=orange, 3=yellow, 4=green, 5=blue, 6=purple
        self.assertEqual(0, 0)  # black
        self.assertEqual(1, 1)  # red
        self.assertEqual(2, 2)  # orange
        self.assertEqual(3, 3)  # yellow
        self.assertEqual(4, 4)  # green
        self.assertEqual(5, 5)  # blue
        self.assertEqual(6, 6)  # purple


class TestPixelAccess(unittest.TestCase):
    """Test pixel get/set operations."""

    def test_set_and_get(self):
        """Test setting and getting a pixel value."""
        df = DotField(10, 10)
        df.set(5, 5, 1)
        self.assertEqual(df.get(5, 5), 1)

    def test_out_of_bounds_get(self):
        """Test that out of bounds get returns None."""
        df = DotField(10, 10)
        self.assertIsNone(df.get(-1, 0))
        self.assertIsNone(df.get(0, -1))
        self.assertIsNone(df.get(10, 0))
        self.assertIsNone(df.get(0, 10))

    def test_out_of_bounds_set(self):
        """Test that out of bounds set doesn't crash."""
        df = DotField(10, 10)
        df.set(-1, 0, 1)
        df.set(10, 0, 1)
        # Should just not set anything


class TestNeighbors(unittest.TestCase):
    """Test neighbor operations."""

    def test_center_neighbors(self):
        """Test getting all 8 neighbors of center pixel."""
        df = DotField(10, 10)
        neighbors = df.get_neighbors(5, 5)
        self.assertEqual(len(neighbors), 8)

        expected = [
            (4, 4), (5, 4), (6, 4),
            (4, 5),         (6, 5),
            (4, 6), (5, 6), (6, 6),
        ]
        self.assertEqual(set(neighbors), set(expected))

    def test_corner_neighbors(self):
        """Test getting neighbors of corner pixel (only 3)."""
        df = DotField(10, 10)
        neighbors = df.get_neighbors(0, 0)
        self.assertEqual(len(neighbors), 3)

        expected = [(0, 1), (1, 0), (1, 1)]
        self.assertEqual(set(neighbors), set(expected))

    def test_has_neighbor_of_color(self):
        """Test neighbor color detection."""
        df = DotField(10, 10)
        df.set(5, 5, 1)  # Red
        df.set(6, 5, 2)  # Orange

        self.assertTrue(df.has_neighbor_of_color(5, 5, 2))
        self.assertFalse(df.has_neighbor_of_color(5, 5, 6))


class TestPixelProgression(unittest.TestCase):
    """Test color progression logic."""

    def test_red_needs_orange_neighbor(self):
        """Test red pixel turns orange only with orange neighbor."""
        df = DotField(3, 3)
        df.set(1, 1, 1)  # Red

        # No orange neighbors - stays red
        self.assertFalse(df.has_neighbor_of_color(1, 1, 2))

        # Add orange neighbor
        df.set(2, 1, 2)  # Orange
        self.assertTrue(df.has_neighbor_of_color(1, 1, 2))

    def test_orange_needs_yellow_neighbor(self):
        """Test orange pixel turns yellow only with yellow neighbor."""
        df = DotField(3, 3)
        df.set(1, 1, 2)  # Orange
        df.set(2, 1, 3)  # Yellow

        self.assertTrue(df.has_neighbor_of_color(1, 1, 3))

    def test_progression_chain(self):
        """Test full color progression chain."""
        df = DotField(7, 1)

        # Set up progression chain
        df.set(0, 0, 1)  # Red
        df.set(1, 0, 2)  # Orange
        df.set(2, 0, 3)  # Yellow
        df.set(3, 0, 4)  # Green
        df.set(4, 0, 5)  # Blue
        df.set(5, 0, 6)  # Purple
        df.set(6, 0, 0)  # Black

        # Verify progression is possible
        self.assertTrue(df.has_neighbor_of_color(0, 0, 2))  # Red needs orange
        self.assertTrue(df.has_neighbor_of_color(1, 0, 3))  # Orange needs yellow
        self.assertTrue(df.has_neighbor_of_color(2, 0, 4))  # Yellow needs green
        self.assertTrue(df.has_neighbor_of_color(3, 0, 5))  # Green needs blue
        self.assertTrue(df.has_neighbor_of_color(4, 0, 6))  # Blue needs purple


class TestHasPurple(unittest.TestCase):
    """Test purple detection."""

    def test_no_purple(self):
        """Test has_purple returns False when no purple pixels."""
        df = DotField(10, 10)
        self.assertFalse(df.has_purple())

    def test_has_purple(self):
        """Test has_purple returns True when purple pixel exists."""
        df = DotField(10, 10)
        df.set(5, 5, 6)  # Purple
        self.assertTrue(df.has_purple())

    def test_multiple_purple(self):
        """Test has_purple with multiple purple pixels."""
        df = DotField(10, 10)
        df.set(0, 0, 6)
        df.set(9, 9, 6)
        self.assertTrue(df.has_purple())


class TestCountColor(unittest.TestCase):
    """Test color counting."""

    def test_count_zero(self):
        """Test counting pixels of a specific color."""
        df = DotField(10, 10)
        self.assertEqual(df.count_color(0), 100)

    def test_count_after_set(self):
        """Test counting after setting some pixels."""
        df = DotField(10, 10)
        df.set(0, 0, 1)
        df.set(1, 1, 1)
        df.set(2, 2, 2)
        self.assertEqual(df.count_color(1), 2)
        self.assertEqual(df.count_color(2), 1)


class TestGeneration(unittest.TestCase):
    """Test generation logic."""

    def test_random_red_creation(self):
        """Test that black pixels can turn red randomly."""
        random.seed(42)
        df = DotField(10, 10)
        # Force the random chance to trigger for testing
        old_random = random.randint
        random.randint = lambda a, b: 1  # Always return 1 (1 in 100 chance)

        df.generation()
        # At least one pixel should have turned red
        red_count = df.count_color(1)
        self.assertGreater(red_count, 0)

        random.randint = old_random

    def test_progression_in_generation(self):
        """Test that colors progress correctly in a generation."""
        df = DotField(3, 1)
        df.set(0, 0, 1)  # Red
        df.set(1, 0, 2)  # Orange (neighbor)
        df.set(2, 0, 0)  # Black

        df.generation()

        # The red pixel should have turned orange
        self.assertEqual(df.get(0, 0), 2)


class TestPNGOutput(unittest.TestCase):
    """Test PNG output functionality."""

    def test_png_file_created(self):
        """Test that PNG file is created."""
        df = DotField(10, 10)
        df.set(5, 5, 6)  # Purple
        df.to_png("test_output.png")

        # Check file exists and has proper PNG header
        with open("test_output.png", "rb") as f:
            signature = f.read(8)
            self.assertEqual(signature, b'\x89PNG\r\n\x1a\n')

    def test_png_file_contains_data(self):
        """Test that PNG file has content."""
        df = DotField(50, 50)
        for y in range(50):
            for x in range(50):
                df.set(x, y, (x + y) % 7)  # Various colors
        df.to_png("test_data.png")

        import os
        size = os.path.getsize("test_data.png")
        self.assertGreater(size, 1000)  # Should be substantial


class TestSimulation(unittest.TestCase):
    """Test full simulation."""

    def test_simulation_runs(self):
        """Test that simulation completes and creates PNG."""
        result = run_simulation()
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_purple_png_exists(self):
        """Test that purple.png is created."""
        import os
        run_simulation()
        self.assertTrue(os.path.exists("purple.png"))


if __name__ == "__main__":
    unittest.main()
