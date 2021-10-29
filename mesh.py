import logging
from buffers import OneToManyConnectionTable, NodeBuffer

class Kernel():

    def __init__(self):
        self.__node_buffer = NodeBuffer()
        self.__face_buffer = OneToManyConnectionTable()

    @property
    def vertex_count(self):
        return self.__node_buffer.vertex_count

    @property
    def node_count(self):
        return self.__node_buffer.node_count

    @property
    def face_count(self):
        return self.__face_buffer.count
    
    def vertices(self):
        return self.__node_buffer.vertices()

    def __get_next_free_face_index(self):
        index = 0
        while True:
            if self.__face_buffer.read_connection(index) is None:
                return index
            else:
                index += 1


    def add_new_face(self, vertices):
        indices = [self.__node_buffer.add_vertex(vertex) for vertex in vertices]
        face_index = self.__get_next_free_face_index()
        self.__face_buffer.create_connection(face_index)
        self.__face_buffer.update_connection(face_index, *indices)

        return face_index

    def remove_face(self, face_index):

        # read out face vertices
        indices = self.__face_buffer.read_connection(face_index)

        if indices is None:
            return False

        self.__face_buffer.delete_connection(face_index)

        # remove vertices from nodebuffer
        return all([self.__node_buffer.remove_vertex(index) for index in indices])

    def faces(self):
        return self.__face_buffer.values()

    def face_indices(self):
        return list(self.__face_buffer.keys())

    def face_vertices(self, face_index):
        indices = self.__face_buffer.read_connection(face_index)
        if indices is None: return None

        return [self.__node_buffer.get_vertex(index) for index in indices]

    def face_nodes(self, face_index):
        indices = self.__face_buffer.read_connection(face_index)
        if indices is None: return None

        return [self.__node_buffer.get_parent_node(index) for index in indices]

    def __face_edge(self, face_index, edge_index):
        verts = self.face_vertices(face_index)
        return (verts[edge_index], verts[(edge_index + 1) % len(self.__face_buffer.read_connection(face_index))])

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
        verts = self.face_vertices(face_index)
        zero = [0, 0, 0]
        for vert in verts:
            for i in range(3):
                zero[i] += vert[i]

        return [coord / len(verts) for coord in zero]

    def subdivide_face_constant_quads(self, face_index, recursion_depth):

        # empty index buffer to be filled with result of subdivision
        index_buffer = []

        # get vertices defined in face
        verts = self.face_vertices(face_index)
        vertex_count = len(verts)

        # calculate the face center
        center = self.face_center(face_index)

        # calculate mid points for all edges defined on the face
        edge_mid_points = [self.__point_on_face_edge(face_index, e, 0.5) for e in range(vertex_count)]

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
            index_buffer.append(self.add_new_face([cur_vert, outgoing_edge_mid, center, incoming_edge_mid]))

        # if we have reached the end of recursion, return the whole index buffer
        if recursion_depth <= 1: return index_buffer

        # iterate over index_buffer
        recursive_buffer = []
        for index in index_buffer:
            # recursively subdivide all faces referenced in index_buffer, moving up the recursion chain
            buffer = self.subdivide_face_constant_quads(index, recursion_depth - 1)
            recursive_buffer.extend(buffer)

        return recursive_buffer

    def subdivide_face_quad_grid(self, face_index, x_div, y_div):

        # get vertices defined in face
        verts = self.face_vertices(face_index)
        vertex_count = len(verts)

        # check if the face is a quad
        if vertex_count != 4:
            logging.debug("Tried to grid-subdivide face at index {}, which is not a quad".format(face_index))
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







class FEMMesh():
    """
    A index-based Mesh class, that exposes convenience methods
    to subdivide it's faces and run FEM simulations.
    """

    def __init__(self):
        self.__kernel = Kernel()
        
    @property
    def vertex_count(self):
        return self.__kernel.vertex_count

    @property
    def vertices(self):
        return self.__kernel.vertices()

    @property
    def node_count(self):
        return self.__kernel.node_count

    @property
    def face_count(self):
        return self.__kernel.face_count

    @property
    def faces(self):
        return self.__kernel.faces

    def add_face(self, vertices):
        return self.__kernel.add_new_face(vertices)

    def subdivide_faces(self, n):
        for index in self.__kernel.face_indices():
            self.__kernel.subdivide_face_constant_quads(index, n)

    def clear(self):
        self.__kernel = Kernel()