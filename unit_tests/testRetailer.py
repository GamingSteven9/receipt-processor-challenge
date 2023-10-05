import unittest
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from process import checkRetailer

# python3 unit_tests/testRetailer.py

class testCheckRetailer(unittest.TestCase):
    def testTarget(self):
        self.assertEqual(checkRetailer("Target"), 6, "Should be 6")

    def testM_M_Corner_Market(self):
        self.assertEqual(checkRetailer("M&M Corner Market"), 14, "Should be 14")

if __name__ == '__main__':
    unittest.main()