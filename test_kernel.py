import unittest
from mesh import Kernel
import logging

class TestFaceTopology(unittest.TestCase):
    
    def test_add_face(self):
        logging.info("test_add_face")
        kernel = Kernel()
        index = kernel.add_new_face([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        self.assertEqual(0, index, "Should be 0")
        self.assertEqual(3, kernel.vertex_count)
        self.assertEqual(3, kernel.node_count)
        self.assertEqual(1, kernel.face_count)

    def test_remove_face(self):
        logging.info("test_remove_face")
        kernel = Kernel()

        index = kernel.add_new_face([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        self.assertEqual(0, index, "Should be 0")

        self.assertTrue(kernel.remove_face(index))

        self.assertEqual(0, kernel.vertex_count)
        self.assertEqual(0, kernel.node_count)
        self.assertEqual(0, kernel.face_count)

    def test_constant_quad_subd_triangle(self):
        logging.info("test_constant_quad_subd_triangle")
        kernel = Kernel()
        index = kernel.add_new_face([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])

        indices = kernel.subdivde_face_constant_quads(index, 2, 0)

        self.assertEqual(48, kernel.face_count)

if __name__ == "__main__":
    logging.basicConfig(filename='test_kernel.log', filemode='w', level=logging.INFO)
    unittest.main()