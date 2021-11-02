from mesh import FEMMesh
import rhino3dm


class RhinoIO:

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
            mesh (Rhino.Geometry.Mesh): The rhino mesh to append a new face to
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
        if length == 3:  # Simple triangle
            mesh.Faces.AddFace(vertex_count, vertex_count + 1, vertex_count + 2)

        elif length == 4:  # Simple quad
            mesh.Faces.AddFace(
                vertex_count, vertex_count + 1, vertex_count + 2, vertex_count + 3
            )

        else:  # Some ngon

            # calculate average point of vertices
            average = [0, 0, 0]
            for vert in vertices:
                for i in range(3):
                    average[i] += vert[i]
            average = [coord / length for coord in average]

            # add centroid to mesh
            centroid_index = mesh.Vertices.Add(average[0], average[1], average[2])

            # empty lists to store ngon verts and faces
            ngon_vertex_indices = [vertex_count + i for i in range(length)]
            ngon_face_indices = []

            # iterate over verts, two at a time and add a tringle face with the centroid
            for index in range(len(vertices)):
                cur = index + vertex_count
                next = (index + 1) % length + vertex_count

                face_index = mesh.Faces.AddFace(cur, next, centroid_index)

            # TODO: Sadly Rhino3dm does not support ngons yet :(, in Rhinocommon this would work
            #     ngon_face_indices.append(face_index)

            # # combine the added triangle fan to a ngon
            # ngon = rhino3dm.MeshNgon.Create(ngon_vertex_indices, ngon_face_indices)
            # mesh.Ngons.AddNgon(ngon)

    @staticmethod
    def convert_to_rhino(fem_mesh):
        """
        Converts the given FEMMesh to a rhino3dm.Mesh

        Args:
            fem_mesh (FEMMesh): The mesh to convert

        Returns:
            rhino3dm.Mesh: The converted mesh instance
        """

        # create new, empty rhino mesh
        mesh = rhino3dm.Mesh()

        # iterate over faces in fem_mesh
        for face in fem_mesh.faces():

            # get vertices
            verts = [fem_mesh.get_vertex(index) for index in face]

            # add a new mesh face from the verts
            RhinoIO.__add_new_mesh_face(mesh, verts)

        return mesh

    @staticmethod
    def convert_to_fem(rhino_mesh):
        raise NotImplementedError()

    @staticmethod
    def write_to_file(mesh, filename="output.3dm", version=6):
        """
        Write the given mesh to a rhino (.3dm) file

        Args:
            mesh (FEMMesh | rhino3dm.Mesh): The mesh to write to file
            filename (str | Optional): The name of the file to write (Default: output.3dm)
        """

        # Test if the mesh is a FEMMesh, and convert to rhino mesh
        if isinstance(mesh, FEMMesh):
            mesh = RhinoIO.convert_to_rhino(mesh)

        # Test if the mesh is a rhino mesh that we can write via rhino3dm
        if isinstance(mesh, rhino3dm.Mesh):

            # create a new File3dm instance
            file = rhino3dm.File3dm()

            # Add the mesh to it's object table
            file.Objects.Add(mesh)

            # Try to write the file
            if not file.Write(filename, version):
                print(
                    "RhinoIO.write_to_file ERROR: Failed to write {}".format(filename)
                )
                return False

            return True

        else:
            print("RhinoIO.write_to_file ERROR: {} is not a valid mesh".format(mesh))
            return False
