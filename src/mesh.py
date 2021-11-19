import logging
import math

from numpy.core.numeric import indices
from buffers import OneToManyConnectionTable, NodeBuffer
from geometry import Plane
import numpy as np


class Kernel:
    """
    A Kernel to be used in meshes. It stores vertex, node and face buffers
    and keeps links between them.
    """

    def __init__(self):
        """
        Initialize a new empty Kernel
        """

        self.__node_buffer = NodeBuffer()
        self.__face_buffer = OneToManyConnectionTable()

        # TODO: Implement as a dict from vertex index to face index, and keep in sync
        self.__vertex_face_connection = {}

    @property
    def vertex_count(self):
        """
        The numver of vertices of the kernel

        Returns:
            int: The number of verts
        """
        return self.__node_buffer.vertex_count

    @property
    def node_count(self):
        """
        The number of unique nodes of the kernel

        Returns:
            int: The number of nodes
        """
        return self.__node_buffer.node_count

    @property
    def face_count(self):
        """
        The number of faces of the kernel

        Returns:
            int: The number of faces
        """
        return self.__face_buffer.count

    def get_vertex(self, vertex_index):
        """
        Gets the vertex position for the given index

        Args:
            vertex_index (int): The index of the vertex
        """
        return self.__node_buffer.get_vertex(vertex_index)

    def get_face(self, face_index):
        """
        Gets the face for the given index, if it exists

        Args:
            face_index (int): The index of the face
        """

        return self.__face_buffer.read_connection(face_index).keys()

    def vertices(self):
        """
        A list of all the vertices of the kernel

        Returns:
            list[vertex]: The vertices
        """
        return self.__node_buffer.vertices()

    def __get_next_free_face_index(self):
        index = 0
        while True:
            if self.__face_buffer.read_connection(index) is None:
                return index
            else:
                index += 1

    def add_new_face(self, vertices):
        """
        Adds a new face to the kernel, from the vertices given

        Args:
            vertices (list[vertices]): The vertices of the face

        Returns:
            int: The index of the added face
        """

        # add all vertices to the kernel, and store their indices
        indices = [self.__node_buffer.add_vertex(vertex) for vertex in vertices]

        # obtain the next free face index as a key
        face_index = self.__get_next_free_face_index()

        # link the face index to the added vertices
        self.__face_buffer.create_connection(face_index)
        self.__face_buffer.update_connection(face_index, *indices)

        # link the added vertices to their parent face
        self.__vertex_face_connection.update({index: face_index for index in indices})

        return face_index

    def remove_face(self, face_index):
        """
        Removes the given face from the mesh.
        This will remove the face, it's vertices
        and all parent nodes of the vertices, if they are empty
        after this removal.

        Args:
            face_index (int): The index of the face to remove

        Returns:
            bool: True if they face was removed, False if something went wrong.
        """

        # read out face vertices
        indices = self.__face_buffer.read_connection(face_index)

        # if we don't find vertices, the face probably isn't defined for that index
        if indices is None:
            return False

        # delete face from face buffer
        self.__face_buffer.delete_connection(face_index)

        # delete all vertex-links from vertex-face map
        for index in indices:
            del self.__vertex_face_connection[index]

        # remove vertices from nodebuffer
        return all([self.__node_buffer.remove_vertex(index) for index in indices])

    def faces(self):
        """
        A list of all the faces in the kernel
        """
        return self.__face_buffer.values()

    def face_indices(self):
        """
        A list of the indices of all faces of the mesh

        Returns:
            list[int]: The face indices
        """
        return list(self.__face_buffer.keys())

    def face_vertices(self, face_index):
        """
        A list of all the vertices, stored in the given face

        Args:
            face_index (int): The index of the face, to find the vertices of

        Returns:
            list[vertex]: The vertices of the face
        """

        indices = self.__face_buffer.read_connection(face_index)
        if indices is None:
            return None

        return [self.__node_buffer.get_vertex(index) for index in indices]

    def face_nodes(self, face_index):
        """
        A list of all the parent nodes, for all vertices in the given face

        Args:
            face_index (int): The index of the face to find the nodes of.

        Returns:
            list[int]: The indices of the nodes of the face
        """

        # get the indices of all vertices stored in the face
        indices = self.__face_buffer.read_connection(face_index)
        if indices is None:
            return None

        # return a collection of parent nodes for all vertices
        return [self.__node_buffer.get_parent_node(index) for index in indices]

    def face_neighbors(self, face_index):
        # empty index set for all face indices
        neighbor_indices = set()

        # get all face_nodes
        nodes = self.face_nodes(face_index)

        # get node faces and add to set
        for node in nodes:
            neighbor_indices.add(self.node_faces(node))

        # remove face_index from set, as it's not technically a neighbor
        neighbor_indices.remove(face_index)

        # return neighbor_indices
        return neighbor_indices

        # TODO: Suuuuuuper inefficient way of doing nn search:

        face_nodes_indices = set(self.face_nodes(face_index))
        neighbor_indices = []

        # Iterate over all faces in self
        for index in self.face_indices():
            # Skip if we iterate the face to search neighbors for
            if index == face_index:
                continue

            # Get all nodes for the current face
            cur_nodes_indices = set(self.face_nodes(index))

            # Check if the set intersection of the node indices produces one or more edges
            if len(face_nodes_indices & cur_nodes_indices) < 2:
                continue

            # Append the neighbor index
            neighbor_indices.append(index)

        return neighbor_indices

    def node_neighbors(self, node_index):
        """
        Gets all nodes connected to the given node via an edge

        Args:
            node_index (int): The index of the node

        Returns:
            Iterable[int]: The indices of the connected nodes
        """

        # empty set for neighbor indices
        neighbor_indices = set()

        # get node faces
        faces = self.node_faces(node_index)

        # iterate over node faces
        for face_index in faces:

            # iterate over face edges
            for edge in self.face_edges(face_index):

                # test if the edge is connected to our starting node
                nodes = self.edge_nodes(edge)
                if not node_index in nodes:
                    continue

                # add edge to neighbor_indices
                neighbor_indices.update(nodes)

        # remove node index from neighbors
        neighbor_indices.remove(node_index)

        # return neighbors
        return neighbor_indices

    def parent_face_index(self, vertex_index):
        """
        Gets the parent face index of the given vertex

        Args:
            vertex_index (int): The index of the vertex

        Returns:
            int: The index of the parent face, or None if no parent is definend
        """

        return self.__vertex_face_connection.get(vertex_index)

    def parent_face(self, vertex_index):
        """
        Gets the parent face of the given vertex

        Args:
            vertex_index (int): The index of the vertex

        Returns:
            face: The parent face of the vertex
        """

        return self.__face_buffer[self.parent_face_index(vertex_index)]

    def __face_edge(self, face_index, edge_index):
        verts = self.face_vertices(face_index)
        return (
            verts[edge_index],
            verts[
                (edge_index + 1) % len(self.__face_buffer.read_connection(face_index))
            ],
        )

    def __point_between_points(cls, a, b, t):
        return [v0 + t * (v1 - v0) for v0, v1 in zip(a, b)]

    def __points_between_points(cls, a, b, count):

        # calculate step amount
        step = 1.0 / (count + 1)

        # empty buffer for division points
        div_points = []

        for i in range(count + 2):
            div_points.append(cls.__point_between_points(a, b, i * step))

        return div_points

    def __point_on_face_edge(self, face_index, edge_index, t):
        a, b = self.__face_edge(face_index, edge_index)
        return self.__point_between_points(a, b, t)

    def __points_on_face_edge(self, face_index, edge_index, count):
        a, b = self.__face_edge(face_index, edge_index)
        return self.__points_between_points(a, b, count)

    def face_center(self, face_index):
        """
        Calculates the center of the given face

        Args:
            face_index (int): The index of the face to calculate the center of

        Returns:
            list[float]: The coordinates of the center as a list
        """

        # get the face vertices
        verts = self.face_vertices(face_index)

        # initialize a helper vert at the origin
        zero = [0, 0, 0]

        # iterate over vertices in face
        for vert in verts:

            # add coordinates of vertices together
            for i in range(3):
                zero[i] += vert[i]

        # return averaged vertices
        return [coord / len(verts) for coord in zero]

    def face_edge(self, face_index, edge_index):
        """
        Gets the edge of the face at the given index

        Args:
            face_index (int): The index of the face to get the edge of
            edge_index (int): The index of the edge

        Returns:
            Set[int]: A set of the two vertex indices connected by the edge
        """
        indices = list(self.__face_buffer.read_connection(face_index))
        if indices is None:
            return

        return set([indices[edge_index], indices[(edge_index + 1) % len(indices)]])

    def face_edges(self, face_index):
        """
        Gets all edges of the face at the given index

        Args:
            face_index (int): The index of the face to get the edge of

        Returns:
            List[Set[int]]: A list of sets of the two vertex indices connected by their edge
        """
        return [
            self.face_edge(face_index, i)
            for i in range(len(self.face_vertices(face_index)))
        ]

    def edge_vertices(self, edge):
        """
        Convenience function to return the two vertex positions of a given edge

        Args:
            edge (Set[int]): The edge to get the vertex positions of

        Returns:
            tuple(vertex, vertex): The two vertices, their order is not guaranteed.
        """

        return [self.__node_buffer.get_vertex(i) for i in edge]

    def edge_nodes(self, edge):
        """
        Get the two nodes connected by a given edge

        Args:
            edge (Set[int]): The edge to get the nodes of

        Returns:
            tuple(int, int): The node indices at start and end of the edge
        """

        return [self.__node_buffer.get_parent_node(i) for i in edge]

    def edge_faces(self, edge):
        """
        Find the faces (or the face) that share the given edge

        Args:
            edge (Set[int]): The edge to get the faces of

        Returns:
            tuple(face): One or two faces, or None if the edge is invalid
        """
        return (self.parent_face(index) for index in edge)

    def node_faces(self, node_index):
        """
        Find the faces that share the given node through their vertices.

        Args:
            node_index (int): The index of the node

        Returns:
            List[face]: The faces connected through the node.
        """
        return [
            self.parent_face_index(index)
            for index in self.__node_buffer.get_node_children(node_index)
        ]

    @staticmethod
    def __unitize_coord(coord):
        return coord / np.linalg.norm(coord)

    def face_plane(self, face_index):
        """
        Returns the plane of a given face

        Args:
            face_index (int): The index of the face to subdivide

        Returns:
            Plane: The plane of the face, with origin at the first face vertex
        """

        # Get vertices of face
        verts = self.face_vertices(face_index)

        # extract origin and x axis from vertices
        origin = verts[0]
        x_axis = verts[1] - verts[0]
        y_axis = verts[-1] - verts[0]

        # Make sure y-axis is perpendicular to z-axis by double-crossing
        z_axis = np.cross(x_axis, y_axis)
        y_axis = np.cross(z_axis, x_axis)

        # Unitize axes
        x_axis = self.__unitize_coord(x_axis)
        y_axis = self.__unitize_coord(y_axis)

        # Return the face plane
        return Plane(origin, x_axis, y_axis)

    def subdivide_face_constant_quads(self, face_index, recursion_depth=1):
        """
        Subdivides the given face into n quads, where n is the number of vertices in the face.
        This function can be run recursively by supplying a recursion depth >= 1.

        Args:
            face_index (int): The index of the face to subdivide
            recursion_depth (int | Optional): The number of times the face should be subdivided.

        Returns:
            list (int): The indices of the newly generated faces
        """

        # empty index buffer to be filled with result of subdivision
        index_buffer = []

        # get vertices defined in face
        verts = self.face_vertices(face_index)
        vertex_count = len(verts)

        # calculate the face center
        center = self.face_center(face_index)

        # calculate mid points for all edges defined on the face
        edge_mid_points = [
            self.__point_on_face_edge(face_index, e, 0.5) for e in range(vertex_count)
        ]

        # remove the initial, now subidivided face
        self.remove_face(face_index)

        # iterate over face vertices
        for i in range(vertex_count):

            # store current vert
            cur_vert = verts[i]

            # get outgoing and incoming edge mid points
            outgoing_edge_mid = edge_mid_points[i]
            incoming_edge_mid = edge_mid_points[i - 1]

            # add new quad and append it's index to the index buffer
            index_buffer.append(
                self.add_new_face(
                    [cur_vert, outgoing_edge_mid, center, incoming_edge_mid]
                )
            )

        # if we have reached the end of recursion, return the whole index buffer
        if recursion_depth <= 1:
            return index_buffer

        # iterate over index_buffer
        recursive_buffer = []
        for index in index_buffer:
            # recursively subdivide all faces referenced in index_buffer, moving up the recursion chain
            buffer = self.subdivide_face_constant_quads(index, recursion_depth - 1)
            recursive_buffer.extend(buffer)

        return recursive_buffer

    def subdivide_face_quad_grid(self, face_index, x_div, y_div):
        """
        Subdivide the given quad with a grid of x * y cells.

        Args:
            face_index (int): The index of the face to subdivide
            x_div (int): The number of cells in face x-direction
            y_div (int): The number of cells in face y-direction

        Returns:
            list (int): The indices of the newly generated faces
        """

        # get vertices defined in face
        verts = self.face_vertices(face_index)
        vertex_count = len(verts)

        # check if the face is a quad
        if vertex_count != 4:
            logging.debug(
                "Tried to grid-subdivide face at index {}, which is not a quad".format(
                    face_index
                )
            )
            return None

        # calculate point division of edges in face x direction
        top_points = self.__points_on_face_edge(face_index, 0, x_div - 1)
        bottom_points = self.__points_on_face_edge(face_index, 2, x_div - 1)

        # reverse bottom point collection, so indices match up with top collection
        bottom_points.reverse()

        # empty buffer for generated face indices
        face_indices = []

        # remove old face
        self.remove_face(face_index)

        # iterate over point grid
        for i in range(len(top_points) - 1):

            cur_top = top_points[i]
            cur_bottom = bottom_points[i]
            next_top = top_points[i + 1]
            next_bottom = bottom_points[i + 1]

            # generate inner grid points in y direction
            # TODO: This way we generate columns twice, which is quite inefficient
            col_left = self.__points_between_points(cur_top, cur_bottom, y_div - 1)
            col_right = self.__points_between_points(next_top, next_bottom, y_div - 1)

            for j in range(len(col_left) - 1):

                a = col_left[j]
                b = col_right[j]
                c = col_right[j + 1]
                d = col_left[j]

                # add face from corners
                face_indices.append(self.add_new_face([a, b, c, d]))

        return face_indices


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

        return self.__kernel.vertices()

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

        return self.__kernel.faces

    @property
    def face_indices(self):
        """
        A list of all face indices in the mesh.

        Returns:
            list[int]: The indices of the faces
        """

        return self.__kernel.face_indices()

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

        for index in self.__kernel.face_indices():
            self.__kernel.subdivide_face_constant_quads(index, n)

    def clear(self):
        """
        Clear the mesh off all vertices, nodes and faces.
        """

        self.__kernel = Kernel()

    def get_vertex(self, vertex_index):
        """
        Gets the vertex for the given index

        Args:
            index (int): The index of the vertex to get
        """
        return self.__kernel.get_vertex(vertex_index)

    def get_face(self, face_index):
        """
        Gets the face for the given index

        Args:
            index (int): The index of the face to get
        """

        return self.__kernel.get_face(face_index)

    def get_face_plane(self, face_index):
        return self.__kernel.face_plane(face_index)

    def get_face_edges(self, face_index):
        return self.__kernel.face_edges(face_index)

    def get_face_neighbors(self, face_index):
        """
        Gets all the neighbors of the given face.

        Args:
            index (int): The index of the face to get the neighbors of

        Returns:
            list[int]: The indices of the neighboring faces
        """

        return self.__kernel.face_neighbors(face_index)

    def get_face_edge(self, face_index, edge_index):
        return self.__kernel.face_edge(face_index, edge_index)

    def get_edge_vertices(self, edge):
        return self.__kernel.edge_vertices(edge)

    def get_edge_nodes(self, edge):
        return self.__kernel.edge_nodes(edge)

    def get_edge_faces(self, edge):
        return self.__kernel.edge_faces(edge)

    def get_face_from_vertex(self, vertex_index):
        return self.__kernel.parent_face(vertex_index)
