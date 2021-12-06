import numpy as np
from geometry import Plane


def __unit_vector(vector):
    """Returns the unit vector of the vector."""
    return vector / np.linalg.norm(vector)


def __angle_between(v1, v2):
    """Returns the angle in radians between vectors 'v1' and 'v2'::

    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    """
    v1_u = __unit_vector(v1)
    v2_u = __unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def __identity():
    return np.identity(4)


def __translation(vector):
    ident = __identity()
    ident[:, 3] = np.append(vector, [1])
    return ident


def __rotation_matrix_around_x(angle_rad):
    s = np.sin(angle_rad)
    c = np.cos(angle_rad)

    result = __identity()
    result[1:3, 1:3] = np.array([[c, s], [-s, c]])
    return result


def __rotation_matrix_around_y(angle_rad):
    s = np.sin(angle_rad)
    c = np.cos(angle_rad)

    result = __identity()
    result[:3, :3] = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
    return result


def __rotation_matrix_around_z(angle_rad):
    s = np.sin(angle_rad)
    c = np.cos(angle_rad)

    result = __identity()
    result[:2, :2] = np.array([[c, -s], [s, c]])
    return result


def transform_to_worldxy(plane):
    translation = __translation(-plane.origin)

    angle_x = __angle_between(np.array([1, 0, 0]), plane.x_axis)
    angle_z = __angle_between(np.array([0, 0, 1]), plane.z_axis)

    rot_x = __rotation_matrix_around_z(angle_x)
    rot_z = __rotation_matrix_around_x(angle_z)

    # if angle_x == 0.0:
    #     rot = rot_z
    # elif angle_z == 0:
    #     rot = rot_x
    # else:
    #     rot = np.matmul(rot_x, rot_z)

    return rot_z.dot(rot_x).dot(translation)

    rot = np.matmul(rot_x, rot_z)

    return np.matmul(rot, translation)


def transform_point(matrix, point):
    return matrix.dot(np.append(point, [1]))[:3]


# if __name__ == "__main__":
#     plane = Plane(np.array([5, 0, 0]), np.array([1, 0, 0]), np.array([1, 0, 1]))
#     pt = plane.point_at(1, 1, 0)
#     print(pt)
#     print(plane.x_axis, plane.y_axis, plane.z_axis)

#     trans = transform_to_worldxy(plane)

#     pt = transform_point(trans, pt)
#     print(pt)
