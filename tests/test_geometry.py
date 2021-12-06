import unittest
import logging
import numpy as np
from geometry import Plane
from mesh import FEMMesh


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

    def test_plane_input(self):
        plane = Plane(np.array([5, 1, 0]), np.array([1, 0, 0]), np.array([1, 1, 0]))
        print(plane.origin)
        np.testing.assert_array_almost_equal(plane.origin, np.array([5, 1, 0]))
        np.testing.assert_array_almost_equal(plane.x_axis, np.array([1, 0, 0]))
        np.testing.assert_array_almost_equal(plane.y_axis, np.array([0, 1, 0]))
        np.testing.assert_array_almost_equal(plane.z_axis, np.array([0, 0, 1]))

    def test_point_on_edge(self):
        mesh = FEMMesh()
        mesh.add_face([np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0.5, 1, 0])])

        edge = (0, 1)
        np.testing.assert_array_almost_equal(
            np.array([0, 0, 0]), mesh.get_point_on_vertex_edge(edge, 0)
        )
        np.testing.assert_array_almost_equal(
            np.array([1, 0, 0]), mesh.get_point_on_vertex_edge(edge, 1)
        )
        np.testing.assert_array_almost_equal(
            np.array([0.5, 0, 0]), mesh.get_point_on_vertex_edge(edge, 0.5)
        )

    def test_face_plane(self):
        mesh = FEMMesh()
        mesh.add_face([np.array([1, 0, 0]), np.array([4, 0, 0]), np.array([1.5, 1, 0])])

        face_plane = mesh.get_face_plane(0)
        expected_plane = Plane(
            np.array([1, 0, 0]), np.array([1, 0, 0]), np.array([0, 1, 0])
        )

        np.testing.assert_array_almost_equal(face_plane.x_axis, expected_plane.x_axis)
        np.testing.assert_array_almost_equal(face_plane.y_axis, expected_plane.y_axis)
        np.testing.assert_array_almost_equal(face_plane.z_axis, expected_plane.z_axis)


if __name__ == "__main__":
    logging.basicConfig(
        filename="test_output/test_geometry.log", filemode="w", level=logging.INFO
    )
    unittest.main()
