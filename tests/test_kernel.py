import unittest
from mesh import Kernel, FEMMesh
import logging
import numpy as np


class TestFaceTopology(unittest.TestCase):
    def test_add_face(self):
        logging.info("test_add_face")
        kernel = Kernel()
        index = kernel.add_new_face(
            [np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0.5, 1, 0])]
        )
        self.assertEqual(0, index, "Should be 0")
        self.assertEqual(3, kernel.vertex_count)
        self.assertEqual(3, kernel.node_count)
        self.assertEqual(1, kernel.face_count)

    def test_remove_face(self):
        logging.info("test_remove_face")
        kernel = Kernel()

        index = kernel.add_new_face(
            [np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0.5, 1, 0])]
        )
        self.assertEqual(0, index, "Should be 0")

        self.assertTrue(kernel.remove_face(index))

        self.assertEqual(0, kernel.vertex_count)
        self.assertEqual(0, kernel.node_count)
        self.assertEqual(0, kernel.face_count)

    def test_constant_quad_subd_triangle(self):
        logging.info("test_constant_quad_subd_triangle")
        kernel = Kernel()
        index = kernel.add_new_face(
            [np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0.5, 1, 0])]
        )

        kernel.subdivide_face_constant_quads(index, 2)

        self.assertEqual(12, kernel.face_count)  # 3 * 4

    def test_quad_grid_subd(self):
        logging.info("test_quad_grid_subd")

        kernel = Kernel()
        index = kernel.add_new_face(
            [
                np.array([0, 0, 0]),
                np.array([1, 0, 0]),
                np.array([1, 1, 0]),
                np.array([0, 1, 0]),
            ]
        )

        kernel.subdivide_face_quad_grid(index, 2, 3)

        self.assertEqual(6, kernel.face_count)

    def test_mesh_subd_all(self):
        logging.info("test_mesh_subd_all")

        mesh = FEMMesh()
        mesh.add_face([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        mesh.add_face([[1, 0, 0], [2, 0, 0], [2, 1, 0], [1, 1, 0]])

        self.assertEqual(8, mesh.vertex_count)
        self.assertEqual(6, mesh.node_count)
        self.assertEqual(2, mesh.face_count)

        mesh.subdivide_faces(2)

        self.assertEqual(32, mesh.face_count)


if __name__ == "__main__":
    logging.basicConfig(
        filename="test_output/test_kernel.log", filemode="w", level=logging.INFO
    )
    unittest.main()
