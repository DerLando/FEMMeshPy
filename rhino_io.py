from mesh import FEMMesh
import rhino3dm

class RhinoIO():

    """
    Static class to convert from FEMMeshPy to a Rhino.Geometry.Mesh and back.
    Also allows storing meshes as rhino files
    """

    @staticmethod
    def __add_new_mesh_face(mesh, vertices):
        """
        Adds a new mesh face to a given mesh with the given vertices.
        This will add a face regardless of how many points are given,
        and do a fan-triangulation if the face is a ngon.

        Args:
            vertices (List[List[float]]): a list of vertices
        """

        # handle degenerate vertex count
        length = len(vertices)
        if length < 3:
            print("add_new_mesh_face ERROR: Not enough vertices to create face!")
            return

        # store current amount of vertices in mesh
        vertex_count = len(mesh.Vertices)

        # iterate over vertices, add them to the mesh
        for vert in vertices:
            mesh.Vertices.Add(vert[0], vert[1], vert[2])

        # match the face vertex count and add faces accordingly
        if length == 3: # Simple triangle
            mesh.Faces.AddFace(vertex_count, vertex_count + 1, vertex_count + 2)

        elif length == 4: # Simple quad
            mesh.Faces.AddFace(vertex_count, vertex_count + 1, vertex_count + 2, vertex_count + 3)

        else: # Some ngon

            # create a helper polyline to calculate centroid of vertices
            centroid = rhino3dm.Polyline(vertices).CenterPoint()

            # add centroid to mesh
            centroid_index = mesh.Vertices.Add(centroid)

            # empty lists to store ngon verts and faces
            ngon_vertex_indices = [vertex_count + i for i in range(length)]
            ngon_face_indices = []

            # iterate over verts, two at a time and add a tringle face with the centroid
            for index in range(len(vertices)):
                cur = index + vertex_count
                next = (index + 1) % length + vertex_count

                face_index = mesh.Faces.AddFace(cur, next, centroid_index)
                ngon_face_indices.append(face_index)

            # combine the added triangle fan to a ngon
            ngon = rhino3dm.MeshNgon.Create(ngon_vertex_indices, ngon_face_indices)
            mesh.Ngons.AddNgon(ngon)


    @staticmethod
    def convert_to_rhino(fem_mesh):

        # create new, empty rhino mesh
        mesh = rhino3dm.Mesh()

        # iterate over faces in fem_mesh
        for face in fem_mesh.faces():

            # get vertices
            verts = [fem_mesh.get_vertex(index) for index in face]

            RhinoIO.__add_new_mesh_face(mesh, verts)

            print(dir(rhino3dm.File3dm))

        return mesh

    @staticmethod
    def convert_to_fem(rhino_mesh):
        raise NotImplementedError()

    @staticmethod
    def write_to_file(mesh, filename="output.3dm", version=6):
        if isinstance(mesh, FEMMesh):
            mesh = RhinoIO.convert_to_rhino(mesh)
        if isinstance(mesh, rhino3dm.Mesh):
            file = rhino3dm.File3dm()
            file.Objects.Add(mesh)
            file.Write(filename, version)
        
