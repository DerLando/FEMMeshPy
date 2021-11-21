import logging
import math

from kernel import Kernel


class FEMMesh:
    """
    A index-based Mesh class, that exposes convenience methods
    to subdivide it's faces and run FEM simulations.
    """

    def __init__(self):
        """
        Initializes a new, empty instance of the FEMMesh class
        """
        self.__kernel = Kernel()

    # region properties

    @property
    def vertex_count(self):
        """
        The total number of vertices stored in the mesh

        Returns:
            int: The number of vertices
        """

        return self.__kernel.vertex_count

    @property
    def vertices(self):
        """
        A list of all the vertices stored in the mesh

        Returns:
            list[list[float]]: The coordinates of the vertices
        """

        return [
            self.__kernel.get_vertex(vertex_index)
            for vertex_index in self.__kernel.vertices()
        ]

    @property
    def node_count(self):
        """
        The total number of unique position nodes in the mesh.
        One node can be the parent of multiple vertices stored at that position.

        Returns:
            int: The number of unique nodes
        """

        return self.__kernel.node_count

    @property
    def face_count(self):
        """
        The total number of faces stored in the mesh.

        Returns:
            int: The number of faces
        """

        return self.__kernel.face_count

    @property
    def faces(self):
        """
        A list of all faces stored in the mesh.

        Returns:
            list[list[int]]: Tha faces as collections of vertex indices
        """

        return [
            self.__kernel.get_face(face_index) for face_index in self.__kernel.faces()
        ]

    @property
    def face_indices(self):
        """
        A list of all face indices in the mesh.

        Returns:
            list[int]: The indices of the faces
        """

        return self.__kernel.faces()

    # endregion

    # region public static methods

    @staticmethod
    def polygon(radius, n_sides):
        """
        Creates a n-gon mesh in the shape of a regular Polygon

        Args:
            radius (float): The radius of the polygon
            n_sides(int): The number of sides of the polygon

        Returns:
            FEMMesh: A mesh with a single face, or None in invalid input.
        """

        if n_sides <= 2:
            return None

        angle_step = 2 * math.pi / n_sides

        verts = []

        for i in range(n_sides):
            vert = [
                radius * math.cos(i * angle_step),
                radius * math.sin(i * angle_step),
                0.0,
            ]
            verts.append(vert)

        mesh = FEMMesh()
        mesh.add_face(verts)

        return mesh

    # endregion

    # region topology modifications

    def add_face(self, vertices):
        """
        Adds a new face to the mesh

        Args:
            vertices (list[list[float]]): The vertices of the face to add

        Returns:
            int: The index of the added face
        """

        return self.__kernel.add_new_face(vertices)

    def subdivide_faces(self, n):
        """
        Recursively subdivides all faces in the mesh, n times.

        Args:
            n (int): The number of times to subdivide
        """

        for index in self.__kernel.faces():
            self.__kernel.subdivide_face_constant_quads(index, n)

    def clear(self):
        """
        Clear the mesh off all vertices, nodes and faces.
        """

        self.__kernel = Kernel()

    # endregion

    # region element getters

    def get_vertex(self, vertex_index):
        """
        Gets the vertex for the given index

        Args:
            index (int): The index of the vertex to get
        """
        return self.__kernel.get_vertex(vertex_index)

    def get_node(self, node_index):
        """
        Gets the node at the given index

        Args:
            index (int): The index of the node to get

        Returns:
            list[vertex]: The vertices stored in the node
        """

        return (
            self.__kernel.get_vertex(vertex_index)
            for vertex_index in self.__kernel.get_node(node_index)
        )

    def get_face(self, face_index):
        """
        Gets the face for the given index

        Args:
            index (int): The index of the face to get

        Returns:
            list[vertex]: The vertices stored in the face
        """

        return (
            self.__kernel.get_vertex(vertex_index)
            for vertex_index in self.__kernel.get_face(face_index)
        )

    # endregion

    # region vertex queries

    def get_parent_node_index(self, vertex_index):
        """
        Gets the parent node of a given vertex

        Args:
            vertex_index (int): The index of the vertex

        Returns:
            int: The index of the parent node
        """

        return self.__kernel.parent_node(vertex_index)

    def get_parent_face_index(self, vertex_index):
        """
        Gets the parent face of a given vertex

        Args:
            vertex_index (int): The index of the vertex

        Returns:
            int: The index of the face
        """

        return self.__kernel.parent_face(vertex_index)

    # endregion

    # region node queries

    def get_node_neighbor_indices(self, node_index):
        """
        Gets all nodes connected to the given node, via an edge

        Args:
            node_index (int): The index of the node to query

        Returns:
            list[int]: The indices of the neighbor, nodes
        """

        return self.__kernel.node_neighbors(node_index)

    # endregion

    # region edge queries

    def get_edge_vertices(self, edge):
        return (self.get_vertex(vertex_index) for vertex_index in edge)

    def get_edge_node_indices(self, edge):
        return self.__kernel.edge_nodes(edge)

    def get_edge_face_indices(self, edge):
        return self.__kernel.edge_faces(edge)

    # endregion

    def get_face_plane(self, face_index):
        return self.__kernel.face_plane(face_index)

    def get_face_edges(self, face_index):
        return self.__kernel.face_edges(face_index)

    def get_face_neighbors(self, face_index):
        """
        Gets all the neighbors of the given face. Neighbors are all faxwa
        that share at least one node with the given face.

        Args:
            index (int): The index of the face to get the neighbors of

        Returns:
            list[int]: The indices of the neighboring faces
        """

        return self.__kernel.face_neighbors(face_index)

    def get_face_edge(self, face_index, edge_index):
        return self.__kernel.face_edge(face_index, edge_index)
