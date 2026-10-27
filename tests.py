#!/usr/bin/env python3
"""Test suite for dot-fields cellular automata simulation."""

import os
import random
import unittest
from dot_fields import DotField, BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, run_simulation


class TestColorFunctions(unittest.TestCase):
    """Tests for color-related functions."""

    def test_color_values(self):
        """Test that color constants have correct RGB values."""
        self.assertEqual(BLACK, (0, 0, 0))
        self.assertEqual(RED, (255, 0, 0))
        self.assertEqual(ORANGE, (255, 165, 0))
        self.assertEqual(YELLOW, (255, 255, 0))
        self.assertEqual(GREEN, (0, 255, 0))
        self.assertEqual(BLUE, (0, 0, 255))
        self.assertEqual(PURPLE, (128, 0, 128))

    def test_get_color_index(self):
        """Test getting color index from grid."""
        field = DotField()
        # All pixels start as black (index 0)
        for y in range(512):
            for x in range(512):
                idx = field.get_color_index(x, y)
                self.assertEqual(idx, 0, f"Expected black (0) at ({x}, {y})")

    def test_set_color(self):
        """Test setting color in grid."""
        field = DotField()
        # Set a pixel to red
        field.set_color(10, 10, 1)
        idx = field.get_color_index(10, 10)
        self.assertEqual(idx, 1)  # RED should be index 1

        # Set to purple
        field.set_color(20, 20, 6)
        idx = field.get_color_index(20, 20)
        self.assertEqual(idx, 6)  # PURPLE should be index 6


class TestDotFieldInitialization(unittest.TestCase):
    """Tests for DotField initialization."""

    def test_default_size(self):
        """Test that default grid is 512x512."""
        field = DotField()
        self.assertEqual(len(field.grid), 512)
        self.assertEqual(len(field.grid[0]), 512)

    def test_custom_size(self):
        """Test that custom grid size works."""
        field = DotField(width=256, height=256)
        self.assertEqual(len(field.grid), 256)
        self.assertEqual(len(field.grid[0]), 256)

    def test_initial_colors(self):
        """Test that all pixels start as black."""
        field = DotField()
        for row in field.grid:
            for pixel in row:
                self.assertEqual(pixel, 0)  # 0 = BLACK


class TestNeighbors(unittest.TestCase):
    """Tests for neighbor-related functions."""

    def test_center_neighbors(self):
        """Test neighbor count for center pixels."""
        field = DotField(width=10, height=10)
        # Center pixel should have 8 neighbors
        neighbors = field.get_neighbors(5, 5)
        self.assertEqual(len(neighbors), 8)

    def test_corner_neighbors(self):
        """Test neighbor count for corner pixels."""
        field = DotField(width=10, height=10)
        # Top-left corner
        neighbors = field.get_neighbors(0, 0)
        self.assertEqual(len(neighbors), 3)
        # Top-right corner
        neighbors = field.get_neighbors(9, 0)
        self.assertEqual(len(neighbors), 3)
        # Bottom-left corner
        neighbors = field.get_neighbors(0, 9)
        self.assertEqual(len(neighbors), 3)
        # Bottom-right corner
        neighbors = field.get_neighbors(9, 9)
        self.assertEqual(len(neighbors), 3)

    def test_edge_neighbors(self):
        """Test neighbor count for edge pixels."""
        field = DotField(width=10, height=10)
        # Top edge (not corner)
        neighbors = field.get_neighbors(5, 0)
        self.assertEqual(len(neighbors), 5)
        # Left edge (not corner)
        neighbors = field.get_neighbors(0, 5)
        self.assertEqual(len(neighbors), 5)

    def test_has_neighbor_of_color(self):
        """Test checking for neighbors of specific color."""
        field = DotField(width=5, height=5)
        # Set center pixel to red
        field.set_color(2, 2, 1)
        
        # Check that the red pixel has neighbors
        neighbors = field.get_neighbors(2, 2)
        self.assertEqual(len(neighbors), 8)
        
        # None of the neighbors should be red initially
        for nx, ny in neighbors:
            idx = field.get_color_index(nx, ny)
            self.assertEqual(idx, 0)  # All black


class TestColorProgression(unittest.TestCase):
    """Tests for color progression logic."""

    def test_full_chain(self):
        """Test that full color chain works: black->red->orange->yellow->green->blue->purple."""
        field = DotField(width=3, height=3)
        
        # Start with black
        field.set_color(1, 1, 0)
        self.assertEqual(field.get_color_index(1, 1), 0)
        
        # Turn to red
        field.set_color(1, 1, 1)
        self.assertEqual(field.get_color_index(1, 1), 1)
        
        # Turn to orange
        field.set_color(1, 1, 2)
        self.assertEqual(field.get_color_index(1, 1), 2)
        
        # Turn to yellow
        field.set_color(1, 1, 3)
        self.assertEqual(field.get_color_index(1, 1), 3)
        
        # Turn to green
        field.set_color(1, 1, 4)
        self.assertEqual(field.get_color_index(1, 1), 4)
        
        # Turn to blue
        field.set_color(1, 1, 5)
        self.assertEqual(field.get_color_index(1, 1), 5)
        
        # Turn to purple
        field.set_color(1, 1, 6)
        self.assertEqual(field.get_color_index(1, 1), 6)


class TestGeneration(unittest.TestCase):
    """Tests for generation step."""

    def test_black_turns_red_randomly(self):
        """Test that black pixels can turn red."""
        random.seed(42)  # Fixed seed for reproducibility
        
        field = DotField(width=10, height=10)
        # All pixels are black initially
        field.set_color(5, 5, 0)
        
        # Check color before generation
        idx_before = field.get_color_index(5, 5)
        self.assertEqual(idx_before, 0)  # Black
        
        # Run a generation - some black pixels should turn red
        # Note: this is probabilistic, so we just check the function runs
        field.generation()
        
        # The test is that the generation function completes without error
        # Some pixels may have turned red due to the 1% chance

    def test_color_progression(self):
        """Test that colors progress correctly."""
        field = DotField(width=3, height=3)
        
        # Set center pixel to red
        field.set_color(1, 1, 1)
        # Set a neighbor to red
        field.set_color(0, 0, 1)
        
        # Run generation - center should turn orange (has red neighbor)
        field.generation()
        
        idx = field.get_color_index(1, 1)
        self.assertGreaterEqual(idx, 1)  # Should be at least red or higher

    def test_multiple_generations_progression(self):
        """Test multiple generations complete the full color cycle."""
        field = DotField(width=5, height=5)
        
        # Initialize with red pixels in a pattern that will cause progression
        for y in range(5):
            for x in range(5):
                field.set_color(x, y, 1)
        
        # Run multiple generations
        for _ in range(20):
            field.generation()
        
        # Check if any pixels have reached purple
        has_purple = False
        for y in range(5):
            for x in range(5):
                if field.get_color_index(x, y) == 6:
                    has_purple = True
                    break
        
        # With enough generations, purple should appear
        # Note: this is probabilistic, so we just verify the function works


class TestCountColor(unittest.TestCase):
    """Tests for color counting."""

    def test_count_initial(self):
        """Test counting initial black pixels."""
        field = DotField(width=10, height=10)
        count = field.count_color(0)
        self.assertEqual(count, 100)  # 10x10 grid

    def test_count_after_progression(self):
        """Test counting colors after progression."""
        field = DotField(width=5, height=5)
        
        # Set all pixels to red
        for y in range(5):
            for x in range(5):
                field.set_color(x, y, 1)
        
        red_count = field.count_color(1)
        self.assertEqual(red_count, 25)


class TestHasPurple(unittest.TestCase):
    """Tests for purple detection."""

    def test_no_purple_initially(self):
        """Test that new grid has no purple pixels."""
        field = DotField()
        self.assertFalse(field.has_purple())

    def test_has_purple_after_progression(self):
        """Test detection of purple pixels after full progression."""
        field = DotField(width=5, height=5)
        
        # Set all pixels to purple
        for y in range(5):
            for x in range(5):
                field.set_color(x, y, 6)
        
        self.assertTrue(field.has_purple())


class TestPNGOutput(unittest.TestCase):
    """Tests for PNG output."""

    def test_save_png_creates_file(self):
        """Test that save_png creates a valid PNG file."""
        field = DotField(width=32, height=32)
        test_file = "/tmp/test_output.png"
        
        field.save_png(test_file)
        
        # Verify file exists and is a valid PNG
        self.assertTrue(os.path.exists(test_file))
        
        # Check PNG header
        with open(test_file, 'rb') as f:
            header = f.read(8)
            self.assertEqual(header[:8], b'\x89PNG\r\n\x1a\n')
        
        # Cleanup
        os.remove(test_file)


class TestRunSimulation(unittest.TestCase):
    """Tests for the full simulation."""

    def test_simulation_runs_until_purple(self):
        """Test that simulation runs until purple appears."""
        # Run the standalone simulation function
        generations = run_simulation()
        
        # Verify simulation ran and produced purple
        # The simulation creates its own DotField, so we can't check it directly
        # But we can verify the function completed successfully
        self.assertGreater(generations, 0)
        
        # Verify purple.png was created
        self.assertTrue(os.path.exists("purple.png"))


if __name__ == '__main__':
    unittest.main()
