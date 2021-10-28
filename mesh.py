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

    def __get_next_free_face_index(self):
        index = 0
        while True:
            if self.__face_buffer.read_connection(index) is None:
                return index
            else:
                index += 1


    def add_new_face(self, vertices):
        # TODO: It's dangerous to give out old indices here I think. 
        # TODO: Maybe it's actually fine and we just have to be careful to not re-use outdated indices
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

        # TODO: This is NOT a clean solution, we have no good way to ask the buffer how many valid faces there are.
        # set face entry to None
        # self.__face_buffer.update_connection(face_index, None)
        self.__face_buffer.delete_connection(face_index)

        # remove vertices from nodebuffer
        return all([self.__node_buffer.remove_vertex(index) for index in indices])

    def faces(self):
        return self.__face_buffer.values()

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

    def __point_on_face_edge(self, face_index, edge_index, t):
        a, b = self.__face_edge(face_index, edge_index)
        return self.__point_between_points(a, b, t)

    def face_center(self, face_index):
        verts = self.face_vertices(face_index)
        zero = [0, 0, 0]
        for vert in verts:
            for i in range(3):
                zero[i] += vert[i]

        return [coord / len(verts) for coord in zero]

    def __subdivide_face_constant_quads_odd(self, face_index, recursion_depth):

        # empty index buffer to be filled with result of subdivision
        index_buffer = []

        # get vertices defined in face
        # TODO: How can we have a None face_index here?
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
        if recursion_depth <= 0: return index_buffer

        # iterate over index_buffer
        recursive_buffer = []
        for index in index_buffer:
            # recursively subdivide all faces referenced in index_buffer, moving up the recursion chain
            buffer = self.__subdivide_face_constant_quads_odd(index, recursion_depth - 1)
            recursive_buffer.extend(buffer)

        return recursive_buffer

    def __subdivide_face_constant_quads_even(self, face_index, even_div, odd_div):
        raise NotImplementedError

    def subdivde_face_constant_quads(self, face_index, even_div, odd_div):
        if len(self.face_vertices(face_index)) % 2 == 1:
            return self.__subdivide_face_constant_quads_odd(face_index, even_div)
        else:
            return self.__subdivide_face_constant_quads_even(face_index, even_div, odd_div)


class Mesh():

    def __init__(self):
        self.__kernel = Kernel()
        