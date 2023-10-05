import unittest
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from process import checkPurchaseTime

# python3 unit_tests/testPurchaseTime.py

class testCheckRetailer(unittest.TestCase):
    def testTarget(self):
        self.assertEqual(checkPurchaseTime("13:01"), 0, "Should be 0")

    def testM_M_Corner_Market(self):
        self.assertEqual(checkPurchaseTime("14:33"), 10, "Should be 10")

if __name__ == '__main__':
    unittest.main()