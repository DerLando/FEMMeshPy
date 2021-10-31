import unittest
import logging
from rhino_io import RhinoIO
from mesh import FEMMesh

class TestConnectionTable(unittest.TestCase):

    def test_fem_to_rhino(self):

        logging.info("test_fem_to_rhino")

        mesh = FEMMesh.polygon(5, 4)

        rhino_mesh = RhinoIO.convert_to_rhino(mesh)

        self.assertEqual(mesh.face_count, rhino_mesh.Faces.Count)
        self.assertEqual(mesh.vertex_count, len(rhino_mesh.Vertices))

        for i in range(mesh.vertex_count):
            self.assertAlmostEqual(mesh.get_vertex(i)[0], rhino_mesh.Vertices[i].X)
            self.assertAlmostEqual(mesh.get_vertex(i)[1], rhino_mesh.Vertices[i].Y)
            self.assertAlmostEqual(mesh.get_vertex(i)[2], rhino_mesh.Vertices[i].Z)

        # RhinoIO.write_to_file(rhino_mesh, filename="test_output/fem_to_rhino.3dm")

if __name__ == "__main__":
    logging.basicConfig(filename='test_output/test_io.log', filemode='w', level=logging.INFO)
    unittest.main()