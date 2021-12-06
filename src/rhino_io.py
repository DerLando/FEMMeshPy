from mesh import FEMMesh
import rhino3dm
import json
import pickle


class MeshBuffer(object):
    def __init__(self, fem_mesh):

        # shrink fem_mesh buffers
        fem_mesh.shrink_buffers()

        coords = []
        for vert in fem_mesh.vertices:
            for coord in vert:
                coords.append(float(round(coord, 3)))

        self.coords = coords
        self.faces = [list(face) for face in fem_mesh.faces]


class RhinoIO:

    """
    Static class to convert from FEMMeshPy to a Rhino.Geometry.Mesh and back.
    Also allows storing meshes as rhino files
    """

    @staticmethod
    def __vertex_to_point3d(vertex):
        return rhino3dm.Point3d(vertex[0], vertex[1], vertex[2])

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

    def __add_layer_to_file3dm(file3dm, name):
        layer = rhino3dm.Layer()
        layer.Name = name

        return file3dm.Layers.Add(layer)

    @staticmethod
    def __write_debug_information(file3dm, fem_mesh):
        """
        Write the connectivity information of the given fem_mesh, to the rhino file.
        Connectivity info is stored in text dots

        Args:
            file3dm (File3dm): The rhino file in memory
            fem_mesh (FEMMesh): The mesh to write debug info for

        Returns:
            bool: True on Success, False if something went wrong
        """

        node_layer_index = RhinoIO.__add_layer_to_file3dm(file3dm, "Nodes")
        face_layer_index = RhinoIO.__add_layer_to_file3dm(file3dm, "Faces")
        edge_layer_index = RhinoIO.__add_layer_to_file3dm(file3dm, "Edges")

        # node_color = draw.Color.FromArgb(230, 79, 225)
        # edge_color = draw.Color.FromArgb(55, 230, 206)
        # face_color = draw.Color.FromArgb(230, 203, 101)

        node_attrs = rhino3dm.ObjectAttributes()
        node_attrs.LayerIndex = node_layer_index

        for node_index in fem_mesh.node_indices:
            vertex_indices = fem_mesh.get_node_indices(node_index)
            file3dm.Objects.AddTextDot(
                str(vertex_indices),
                RhinoIO.__vertex_to_point3d(
                    fem_mesh.get_vertex(next(iter(vertex_indices)))
                ),
                node_attrs,
            )

        face_attrs = rhino3dm.ObjectAttributes()
        face_attrs.LayerIndex = face_layer_index

        for face_index in fem_mesh.face_indices:
            vertex_indices = fem_mesh.get_face_indices(face_index)
            center = fem_mesh.get_face_center(face_index)
            file3dm.Objects.AddTextDot(
                str(vertex_indices), RhinoIO.__vertex_to_point3d(center), face_attrs
            )

        # edge_attrs = rhino3dm.ObjectAttributes()
        # edge_attrs.LayerIndex = edge_layer_index

        # for edge in fem_mesh.node_edges:
        #     center = fem_mesh.get_point_on_node_edge(edge, 0.5)
        #     file3dm.Objects.AddTextDot(
        #         str(edge), RhinoIO.__vertex_to_point3d(center), edge_attrs
        #     )

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
        for face in fem_mesh.faces:

            # get vertices
            verts = [fem_mesh.get_vertex(index) for index in face]

            # add a new mesh face from the verts
            RhinoIO.__add_new_mesh_face(mesh, verts)

        return mesh

    @staticmethod
    def convert_to_fem(rhino_mesh):
        raise NotImplementedError()

    @staticmethod
    def convert_to_json(fem_mesh):
        r_mesh = RhinoIO.convert_to_rhino(fem_mesh)
        return r_mesh.Encode()

    @staticmethod
    def convert_to_bytes(fem_mesh):
        return pickle.dumps(MeshBuffer(fem_mesh), 2)

    @staticmethod
    def write_to_file(mesh, filename="output.3dm", version=6, debug=False):
        """
        Write the given mesh to a rhino (.3dm) file

        Args:
            mesh (FEMMesh | rhino3dm.Mesh): The mesh to write to file
            filename (str | Optional): The name of the file to write (Default: output.3dm)
            debug (bool | Optional): Also write debug information to the rhino file

        Returns:
            bool: True on success, False on failure
        """

        # Test if the mesh is a FEMMesh, and convert to rhino mesh
        if isinstance(mesh, FEMMesh):
            # TODO: Make this less hacky
            fem_mesh = mesh
            mesh = RhinoIO.convert_to_rhino(mesh)

        # Test if the mesh is a rhino mesh that we can write via rhino3dm
        if isinstance(mesh, rhino3dm.Mesh):

            # create a new File3dm instance
            file = rhino3dm.File3dm()

            # Add the mesh to it's object table
            mesh_layer_index = RhinoIO.__add_layer_to_file3dm(file, "Mesh")
            mesh_attrs = rhino3dm.ObjectAttributes()
            mesh_attrs.LayerIndex = mesh_layer_index
            file.Objects.Add(mesh, mesh_attrs)

            # Try to write debug information to file
            if debug:
                RhinoIO.__write_debug_information(file, fem_mesh)

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
