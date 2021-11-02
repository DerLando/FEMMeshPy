import numpy as np


class Plane:
    """
    A Plane primitive.
    It is internally represented as a parametrical matrix: [U, V, N, Q],
    where Q is the origin and u, v, n are the x, y, z axes.
    This allows for easy transforming from carthesian to plane space and back.
    """

    def __init__(self, origin, x_axis, y_axis):
        """
        Creates a new plane instance.

        Args:
            origin (array-like): The position where the plane will be located.
            x_axis (array-like): The x-axis direction of the plane. Needs to be normalized.
            y_axis (array-like): The y-axis direction of the plane. Needs to be normalized.
        """
        normal = np.cross(x_axis, y_axis)

        matrix = np.array([x_axis, y_axis, normal, origin])
        matrix = matrix.transpose()
        self.__matrix = np.vstack([matrix, np.array([0, 0, 0, 1])])

    @property
    def x_axis(self):
        """
        The x-axis of the plane

        Returns:
            array-like: The x-axis
        """

        return self.__matrix[0, :-1]

    @property
    def y_axis(self):
        """
        The y_axis of the plane

        Returns:
            array-like: The y-axis
        """

        return self.__matrix[1, :-1]

    @property
    def z_axis(self):
        """
        The z_axis of the plan

        Returns:
            array-like: The z_axis
        """

        return self.__matrix[2, :-1]

    @property
    def origin(self):
        """
        The origin location of the plane

        Returns:
            array-like: The origin
        """

        return self.__matrix[3, :-1]

    @staticmethod
    def __to_homogenous(carthesian_vector):
        """
        Converts a carthesion vector (x, y, z) to a homogenous one (x, y, z, 1).
        This is mainly used to allow Matrix operations with 4x4 Matrices.

        Args:
            carthesian_vector (array-like): The vector to convert

        Returns:
            array-like: The vector in homogenous coordinates.
        """
        return np.append(carthesian_vector, [1])

    @staticmethod
    def __to_carthesian(homogenous_vector):
        """
        Converts a homogenous vdctor (x, y, z, 1) to a carthesion vector (x, y, z), by omitting the last value.

        Args:
            homogenous_vector (array-like): The vector to convert

        Returns:
            array-like: The vector in carthesian coordinates.
        """
        return homogenous_vector[:-1]

    def __evaluate(self, u, v, n):
        """
        Evaluate the plane at the given coordinates in plane space.

        Args:
            u (float): x-coordinate in plane space
            v (float): y-coordinate in plane space
            n (float): z-coordinate in plane space

        Returns:
            array-like: The evaluated point in carthesian space.
        """

        return self.__matrix.dot(Plane.__to_homogenous(np.array([u, v, n])))

    def point_at(self, u, v, n):
        """
        Evaluate a point at the given coordinates in plane space.

        Args:
            u (float): x-coordinate in plane space
            v (float): y-coordinate in plane space
            n (float): z-coordinate in plane space

        Returns:
            array-like: The evaluated point in carthesian space.
        """

        return Plane.__to_carthesian(self.__evaluate(u, v, n))

    def convert_to_plane_space(self, vector):
        """
        Converts a point from carthesian to plane space.

        Args:
            vector (array-like): The point to convert.

        Returns:
            array-like: A point in plane coordinates
        """

        inverse = np.linalg.inv(self.__matrix)
        return Plane.__to_carthesian(inverse.dot(Plane.__to_homogenous(vector)))
