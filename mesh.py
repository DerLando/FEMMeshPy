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

    def add_new_face(self, vertices):
        indices = [self.__node_buffer.add_vertex(vertex) for vertex in vertices]
        face_index = self.__face_buffer.count
        self.__face_buffer.create_connection(face_index)
        self.__face_buffer.update_connection(face_index, *indices)

        return face_index

    def remove_face(self, face_index):

        # read out face vertices
        indices = self.__face_buffer.read_connection(face_index)

        if indices is None:
            return False

        # remove face entry from face buffer
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

    def subdivde_face_center_quad_fan(self, face_index):
        verts = self.face_vertices(face_index)
        vertex_count = len(verts)
        center = self.face_center(face_index)
        edge_mid_points = [self.__point_on_face_edge(face_index, e, 0.5) for e in range(vertex_count)]

        new_face_indices = []
        for i in range(vertex_count):
            cur_vert = verts[i]
            outgoing_edge_mid = edge_mid_points[i]
            incoming_edge_mid = edge_mid_points[i - 1]

            new_face_indices.append(self.add_new_face([cur_vert, outgoing_edge_mid, center, incoming_edge_mid]))

        self.remove_face(face_index)

        return new_face_indices


class Mesh():

    def __init__(self):
        self.__kernel = Kernel()