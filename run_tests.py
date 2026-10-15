#!/usr/bin/env python3
"""
Test suite for dot-fields cellular automata simulation.

Run with: python run_tests.py
"""

import unittest
import random
import os
import sys
from dot_fields import (
    DotField,
    BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE,
    COLORS, run_simulation
)


class TestDotFieldInitialization(unittest.TestCase):
    """Test DotField initialization."""

    def test_default_size(self):
        """Test that default grid is 512x512."""
        df = DotField()
        self.assertEqual(df.width, 512)
        self.assertEqual(df.height, 512)

    def test_custom_size(self):
        """Test that custom grid size works."""
        df = DotField(10, 20)
        self.assertEqual(df.width, 10)
        self.assertEqual(df.height, 20)

    def test_initial_colors(self):
        """Test that all pixels start as black."""
        df = DotField(10, 10)
        for y in range(df.height):
            for x in range(df.width):
                self.assertEqual(df.get_color_index(x, y), 0)
                self.assertEqual(df.get_color(x, y), BLACK)


class TestColorFunctions(unittest.TestCase):
    """Test color-related functions."""

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
        df = DotField(5, 5)
        df.set_color(2, 2, 1)  # RED
        self.assertEqual(df.get_color_index(2, 2), 1)

    def test_set_color(self):
        """Test setting color in grid."""
        df = DotField(5, 5)
        df.set_color(0, 0, 3)  # YELLOW
        self.assertEqual(df.get_color_index(0, 0), 3)
        self.assertEqual(df.get_color(0, 0), YELLOW)


class TestNeighbors(unittest.TestCase):
    """Test neighbor-related functions."""

    def test_corner_neighbors(self):
        """Test neighbor count for corner pixels."""
        df = DotField(5, 5)
        # Top-left corner (0, 0)
        neighbors = df.get_neighbors(0, 0)
        self.assertEqual(len(neighbors), 3)
        self.assertIn((1, 0), neighbors)
        self.assertIn((0, 1), neighbors)
        self.assertIn((1, 1), neighbors)

    def test_edge_neighbors(self):
        """Test neighbor count for edge pixels."""
        df = DotField(5, 5)
        # Top edge (2, 0)
        neighbors = df.get_neighbors(2, 0)
        self.assertEqual(len(neighbors), 5)

    def test_center_neighbors(self):
        """Test neighbor count for center pixels."""
        df = DotField(5, 5)
        # Center (2, 2)
        neighbors = df.get_neighbors(2, 2)
        self.assertEqual(len(neighbors), 8)

    def test_has_neighbor_of_color(self):
        """Test checking for neighbors of specific color."""
        df = DotField(5, 5)
        df.set_color(2, 2, 1)  # RED at center
        df.set_color(3, 2, 1)  # RED to the right
        
        # (2, 2) should have a RED neighbor
        self.assertTrue(df.has_neighbor_of_color(2, 2, 1))
        
        # (0, 0) should not have a RED neighbor
        self.assertFalse(df.has_neighbor_of_color(0, 0, 1))


class TestGeneration(unittest.TestCase):
    """Test the generation() method."""

    def test_black_turns_red_randomly(self):
        """Test that black pixels can turn red."""
        # Set seed for reproducibility
        random.seed(42)
        
        df = DotField(10, 10)
        df.set_color(5, 5, 0)  # Ensure it's black
        
        # Generate enough times to trigger the 1% chance
        for _ in range(200):
            df.generation()
            if df.get_color_index(5, 5) == 1:  # RED
                break
        
        # After many generations, it should have turned red
        self.assertGreaterEqual(df.get_color_index(5, 5), 1)

    def test_color_progression(self):
        """Test that colors progress correctly."""
        df = DotField(5, 5)
        
        # Set up a pattern where colors should advance
        # Place two RED pixels next to each other
        df.set_color(2, 2, 1)  # RED
        df.set_color(3, 2, 1)  # RED
        
        # Run generation
        df.generation()
        
        # The neighbors should turn orange
        self.assertEqual(df.get_color_index(2, 2), 2)  # Should be ORANGE
        self.assertEqual(df.get_color_index(3, 2), 2)  # Should be ORANGE

    def test_multiple_generations_progression(self):
        """Test multiple generations complete the full color cycle."""
        df = DotField(10, 10)
        
        # Place two RED pixels next to each other
        df.set_color(5, 5, 1)  # RED
        df.set_color(6, 5, 1)  # RED
        
        # Run 5 generations to go from RED to PURPLE
        for _ in range(5):
            df.generation()
        
        # Should have reached at least purple
        max_color = max(df.get_color_index(x, y) 
                       for y in range(df.height) 
                       for x in range(df.width))
        self.assertGreaterEqual(max_color, 6)


class TestHasPurple(unittest.TestCase):
    """Test the has_purple() method."""

    def test_no_purple_initially(self):
        """Test that new grid has no purple pixels."""
        df = DotField(10, 10)
        self.assertFalse(df.has_purple())

    def test_has_purple_after_progression(self):
        """Test detection of purple pixels after full progression."""
        df = DotField(10, 10)
        
        # Set up pattern that will become purple
        df.set_color(5, 5, 6)  # PURPLE directly
        self.assertTrue(df.has_purple())


class TestCountColor(unittest.TestCase):
    """Test the count_color() method."""

    def test_count_initial(self):
        """Test counting initial black pixels."""
        df = DotField(10, 10)
        self.assertEqual(df.count_color(0), 100)

    def test_count_after_progression(self):
        """Test counting colors after progression."""
        df = DotField(5, 5)
        df.set_color(2, 2, 1)  # RED
        df.set_color(3, 2, 1)  # RED
        df.set_color(2, 3, 1)  # RED
        
        self.assertEqual(df.count_color(1), 3)


class TestPNGOutput(unittest.TestCase):
    """Test PNG output functionality."""

    def test_save_png_creates_file(self):
        """Test that save_png creates a valid PNG file."""
        df = DotField(10, 10)
        test_file = 'test_output.png'
        
        df.save_png(test_file)
        
        self.assertTrue(os.path.exists(test_file))
        
        # Check PNG header
        with open(test_file, 'rb') as f:
            header = f.read(8)
            self.assertEqual(header, b'\x89PNG\r\n\x1a\n')
        
        # Clean up
        os.remove(test_file)


class TestRunSimulation(unittest.TestCase):
    """Test the run_simulation() function."""

    def test_simulation_runs_until_purple(self):
        """Test that simulation runs until purple appears."""
        # Use a small seed for faster testing
        random.seed(12345)
        
        result = run_simulation()
        
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)
        
        # Verify purple.png was created
        self.assertTrue(os.path.exists('purple.png'))
        
        # Clean up
        if os.path.exists('purple.png'):
            os.remove('purple.png')


class TestColorProgression(unittest.TestCase):
    """Test the complete color progression chain."""

    def test_full_chain(self):
        """Test that full color chain works: black->red->orange->yellow->green->blue->purple."""
        df = DotField(3, 3)
        
        # Place two adjacent RED pixels
        df.set_color(0, 0, 1)  # RED
        df.set_color(1, 0, 1)  # RED
        
        # Gen 1: Should turn orange
        df.generation()
        self.assertEqual(df.get_color_index(0, 0), 2)  # ORANGE
        self.assertEqual(df.get_color_index(1, 0), 2)  # ORANGE
        
        # Gen 2: Should turn yellow
        df.generation()
        self.assertEqual(df.get_color_index(0, 0), 3)  # YELLOW
        self.assertEqual(df.get_color_index(1, 0), 3)  # YELLOW
        
        # Gen 3: Should turn green
        df.generation()
        self.assertEqual(df.get_color_index(0, 0), 4)  # GREEN
        self.assertEqual(df.get_color_index(1, 0), 4)  # GREEN
        
        # Gen 4: Should turn blue
        df.generation()
        self.assertEqual(df.get_color_index(0, 0), 5)  # BLUE
        self.assertEqual(df.get_color_index(1, 0), 5)  # BLUE
        
        # Gen 5: Should turn purple
        df.generation()
        self.assertEqual(df.get_color_index(0, 0), 6)  # PURPLE
        self.assertEqual(df.get_color_index(1, 0), 6)  # PURPLE


def run_all_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*70}")
    
    return len(result.failures) + len(result.errors)


if __name__ == '__main__':
    sys.exit(run_all_tests())
