from rhino_io import RhinoIO
from mesh import FEMMesh
import os


def main():

    mesh = FEMMesh.polygon(1, 5)
    mesh.subdivide_faces(2)

    output_path = os.path.realpath(".\\tests\\test_output\\debug_output.3dm")

    RhinoIO.write_to_file(mesh, filename=output_path, debug=True)


if __name__ == "__main__":
    main()
