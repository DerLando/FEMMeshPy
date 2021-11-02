import unittest
import logging
import numpy as np
from geometry import Plane


class TestFaceTopology(unittest.TestCase):
    def test_plane(self):
        plane = Plane(np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0, 1, 0]))

        np.testing.assert_array_almost_equal(
            np.array([0.5, 1.5, 2.5]), plane.point_at(0.5, 1.5, 2.5)
        )

        test_pt = np.array([0.5, 2.7, -1.7])
        projected = plane.convert_to_plane_space(test_pt)

        np.testing.assert_array_almost_equal(test_pt, projected)

        plane = Plane(np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0, 0, 1]))

        test_pt = np.array([-1.4, 3.2, -2.8])
        projected = plane.convert_to_plane_space(test_pt)

        np.testing.assert_array_almost_equal(np.array([-1.4, -2.8, -3.2]), projected)
        np.testing.assert_array_almost_equal(
            test_pt, plane.point_at(projected[0], projected[1], projected[2])
        )


if __name__ == "__main__":
    logging.basicConfig(
        filename="test_output/test_geometry.log", filemode="w", level=logging.INFO
    )
    unittest.main()
