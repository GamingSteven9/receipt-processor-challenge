import unittest
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from process import checkTotalRound

# python3 unit_tests/testTotalRound.py

class testCheckRetailer(unittest.TestCase):
    def test35point35(self):
        self.assertEqual(checkTotalRound("35.35"), 0, "Should be 0")

    def test9(self):
        self.assertEqual(checkTotalRound("9.00"), 50, "Should be 50")

if __name__ == '__main__':
    unittest.main()