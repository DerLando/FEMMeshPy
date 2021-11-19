import unittest
from mesh import Kernel, FEMMesh
import logging
import numpy as np


class TestFaceQueries(unittest.TestCase):
    def test_face_neighbors(self):

        logging.info("test_face_neighbors")

        mesh = FEMMesh()
        mesh.add_face([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        mesh.subdivide_faces(1)

        for index in mesh.face_indices:
            neighbor_indices = mesh.get_face_neighbors(index)
            self.assertEqual(len(neighbor_indices), 2)

    # TODO: Maybe implement Node-NN and Vertex-NN ?


if __name__ == "__main__":
    unittest.main()
