import unittest
from mesh import Kernel

class TestFaceTopology(unittest.TestCase):
    
    def test_add_face(self):
        kernel = Kernel()
        index = kernel.add_new_face([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        self.assertEqual(0, index, "Should be 0")

        print(kernel.faces())

if __name__ == "__main__":
    unittest.main()