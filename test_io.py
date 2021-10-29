import unittest
import logging
from rhino_io import RhinoIO
from mesh import FEMMesh

class TestConnectionTable(unittest.TestCase):

    def test_fem_to_rhino(self):

        logging.info("test_fem_to_rhino")

        mesh = FEMMesh()
        mesh.add_face([[0,0,0], [1,0,0], [0.5, 0.5, 0]])

        rhino_mesh = RhinoIO.convert_to_rhino(mesh)

        RhinoIO.write_to_file(rhino_mesh, filename="test_output/fem_to_rhino.3dm")

if __name__ == "__main__":
    logging.basicConfig(filename='test_output/test_io.log', filemode='w', level=logging.INFO)
    unittest.main()