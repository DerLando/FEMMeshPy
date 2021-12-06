from mesh import FEMMesh
from rhino_io import RhinoIO
import os

COORDINATES_FRONT_FACE = [[0, 0, 0], [0, 0, 3], [1.5, 0, 4], [3, 0, 3], [3, 0, 0]]


class House:
    def __init__(self, front_points, depth):
        back_points = House.__calculate_house_vertices(front_points, depth)

        self.wireframe = House.__build_house_wireframe(front_points, back_points)

        mesh = FEMMesh()

        for key in self.wireframe:
            if "face" in key:
                mesh.add_face(self.wireframe[key])

        self.mesh = mesh

    @staticmethod
    def __calculate_house_vertices(coordinates_front_face, building_depth):
        """
        Calculates all vertices of the house,
        and returns them as individual lists of points.
        """

        # Calculate coordinates of back face by adding building depth to y
        return [
            [coord[0], coord[1] + building_depth, coord[2]]
            for coord in coordinates_front_face
        ]

    @staticmethod
    def __build_house_wireframe(points_front_face, points_back_face):
        # Empty wireframe dict
        wireframe = {
            "name": "House Detmold",
            "location": "Detmold",
            "face_front": points_front_face,
            "face_back": points_back_face,
        }

        # Side key is made up of identifier 'side' and a number
        side_ident = "face_side"
        side_key = None

        # Add sides of house to mesh, this is achieved by iterating
        # over front and back face vertices in groups of 4 and adding quads
        for i in range(len(points_front_face) - 1):

            # get current and next point of front face
            cur_front = points_front_face[i]
            next_front = points_front_face[i + 1]

            # get current and next point of back face
            cur_back = points_back_face[i]
            next_back = points_back_face[i + 1]

            # assign corners to list
            side_corners = [cur_front, next_front, next_back, cur_back]

            # test if side_key needs to be updated
            update = False
            if side_key in wireframe:  # key exists, but already data there
                if len(wireframe[side_key]) > 0:
                    update = True
            else:  # key does not exist
                update = True

            # update the key if needed
            if update:
                side_key = side_ident + str(i)

            # add the side corners to the wireframe dict, at the correct face
            wireframe[side_key] = side_corners

        return wireframe


def main():
    """
    Task related implementation of Semester project
    """

    # The depth of the building (distance from front to back face)
    building_depth = 5.0

    # Generate House from points and depth
    house = House(COORDINATES_FRONT_FACE, building_depth)

    # Subdivide House faces
    house.mesh.subdivide_faces(3)

    # Write House mesh to rhino file
    output_path = os.path.realpath(".\\tests\\test_output\\task_output.3dm")
    if RhinoIO.write_to_file(house.mesh, output_path):

        # print some feedback
        print("SUCCESS: Wrote task result to {}".format(output_path))


if __name__ == "__main__":
    main()
