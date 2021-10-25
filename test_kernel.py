import unittest
from mesh import Kernel

class TestFaceTopology(unittest.TestCase):
    
    def test_add_face(self):
        kernel = Kernel()
        index = kernel.add_new_face([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        self.assertEqual(0, index, "Should be 0")
        self.assertEqual(3, kernel.vertex_count)
        self.assertEqual(3, kernel.node_count)
        self.assertEqual(1, kernel.face_count)

    def test_remove_face(self):
        kernel = Kernel()

        index = kernel.add_new_face([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]])
        self.assertEqual(0, index, "Should be 0")

        self.assertTrue(kernel.remove_face(index))

        self.assertEqual(0, kernel.vertex_count)
        self.assertEqual(0, kernel.node_count)
        self.assertEqual(0, kernel.face_count)

    def test_constant_quad_subd(self):
        kernel = Kernel()
        index = kernel.add_new_face([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])

        indices = kernel.subdivde_face_center_quad_fan(index)
        self.assertListEqual([[0, 0, 0], [0.5, 0, 0], [0.5, 0.5, 0], [0, 0.5, 0]], kernel.face_vertices(indices[0]), "Should be equal")
        self.assertListEqual([[1, 0, 0], [1, 0.5, 0], [0.5, 0.5, 0], [0.5, 0, 0]], kernel.face_vertices(indices[1]), "Should be equal")
        self.assertListEqual([[1, 1, 0], [0.5, 1, 0], [0.5, 0.5, 0], [1, 0.5, 0]], kernel.face_vertices(indices[2]), "Should be equal")
        self.assertListEqual([[0, 1, 0], [0, 0.5, 0], [0.5, 0.5, 0], [0.5, 1, 0]], kernel.face_vertices(indices[3]), "Should be equal")

        self.assertEqual(4, kernel.face_count)

if __name__ == "__main__":
    unittest.main()