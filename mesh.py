from buffers import OneToManyConnectionTable, NodeBuffer

class Kernel():

    def __init__(self):
        self.__node_buffer = NodeBuffer()
        self.__face_buffer = OneToManyConnectionTable()

    def add_new_face(self, vertices):
        indices = [self.__node_buffer.add_vertex(vertex) for vertex in vertices]
        face_index = self.__face_buffer.count
        self.__face_buffer.create_connection(face_index)
        self.__face_buffer.update_connection(face_index, *indices)

        return face_index

    def faces(self):
        return self.__face_buffer.values()

    def __face_vertices(self, face_index):
        indices = self.__face_buffer.read_connection(face_index)
        if indices is None: return None

        return [self.__node_buffer.get_vertex(index) for index in indices]

    def __face_nodes(self, face_index):
        indices = self.__face_buffer.read_connection(face_index)
        if indices is None: return None

        return [self.__node_buffer.get_parent_node(index) for index in indices]

    def __face_edge(self, face_index, edge_index):
        verts = self.__face_vertices(face_index)
        return (verts[edge_index], verts[edge_index + 1])

    def __point_between_points(cls, a, b, t):
        return [v0 + t * [v1 - v0] for v0, v1 in zip(a, b)]

    def __point_on_face_edge(self, face_index, edge_index, t):
        a, b = self.__face_edge(face_index, edge_index)
        return self.__point_between_points(a, b, t)

class Mesh():

    def __init__(self):
        self.__kernel = Kernel()