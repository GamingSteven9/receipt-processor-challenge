import unittest
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from process import checkPurchaseDate

# python3 unit_tests/testPurchaseDate.py

class testCheckRetailer(unittest.TestCase):
    def testdate2022_01_01(self):
        self.assertEqual(checkPurchaseDate("2022-01-01"), 6, "Should be 6")

    def test2022_03_20(self):
        self.assertEqual(checkPurchaseDate("2022-03-20"), 0, "Should be 0")

if __name__ == '__main__':
    unittest.main()