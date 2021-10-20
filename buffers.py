import math

class OneToManyConnectionTable():
    """
    Convenience mapper Class to generate OneToMany Bindings.
    The class is backed by a dictionary and exposes a CRUD API for safe operations on it.
    """

    def __init__(self):
        # initialize empty backing dictionary
        self.__connections = {}

    def create_connection(self, key):
        """Create a new, empty connection

        Args:
            key (Any): The key for the connection
        """
        # initialize an empty list at the given key
        self.__connections[key] = []

    def read_connection(self, key):
        """Reads the connection data for the given key

        Args:
            key (Any): The key for the connection

        Returns:
            List[Any]: A list of connected values, or None if the key is not found.
        """
        # call dict.get() to return the connection data, or None
        return self.__connections.get(key)

    def update_connection(self, key, *args):
        """Updates a connection with the given arguments.
        If the key is not present in the backing dict, this will do nothing.

        Args:
            key (Any): The key for the connection
        """
        # Test if valid key and exit early if not
        if not key in self.__connections: return

        # Overwrite data stored at key with args
        self.__connections[key] = list(args)

    def delete_connection(self, key, value=None):
        """Deletes all or parts of the connection data for the given key.

        Args:
            key (Any): The key for the connection
            value (Any, optional): The value to delete from the connection. Defaults to None.
        """
        # Check if key exists, and return early if not
        if not key in self.__connections: return

        # Branch depending on the optional value argument
        if value is None: # if we don't have a value, delete all data stored at the key
            del self.__connections[key]
        else:
            # read out the data stored at the key
            values = self.read_connection(key)

            # remove the specified value from the connection, if the value is not contained, this does nothing
            values.remove(value)

    @property
    def count(self):
        return len(self.__connections)

class NodeBuffer():
    """
    A buffer of nodes and vertices. 
    One node can contain multiple vertices.
    This class exposes convenience function to map between nodes and vertices contained within.
    """

    # The equality constant used to determine if two vertices are in the same node.
    __NODE_EQUALITY_EPSILON = 0.01
    __NODE_ROUND_DIGITS = len(str(__NODE_EQUALITY_EPSILON)) - 1

    def __init__(self):
        # Internal backing store of all nodes, nodes are a list of coordinates
        self.__nodes = []
        # Internal backing store of all vertices, vertices are a list of coordinates
        self.__vertices = []
        # Internal table matching one node_index to many vertex_indices
        self.__node_vertex_table = OneToManyConnectionTable()
        # Internal dict matching one vertex position to one node_index
        self.__vertex_node_dict = {}

    @property
    def node_count(self):
        return len(self.__nodes)

    @property
    def vertex_count(self):
        return len(self.__vertices)

    def nodes(self):
        return self.__nodes.copy()

    def __round_vertex(cls, vertex):
        """Rounds the coordinates of a given vertex to the inner equality precision

        Args:
            vertex (List[float]): the vertex coordinates as a list

        Returns:
            List[float]: the rounded coordinate values as a list
        """
        return [round(coord, cls.__NODE_ROUND_DIGITS) for coord in vertex]

    def __vertex_distance(cls, a, b):
        return math.sqrt(sum([v0**2 + v1**2 for v0, v1 in zip(a, b)]))

    def find_closest_node(self, vertex):
        dist = float("inf")
        found = -1
        for index, node in enumerate(self.__nodes):
            cur_dist = self.__vertex_distance(node, vertex)
            if cur_dist < self.__NODE_EQUALITY_EPSILON:
                return (index, node)
            if cur_dist < dist:
                dist = cur_dist
                found = index

        if found == -1:
            return (None, None)

        return (found, self.__nodes[found])

    def add_vertex(self, vertex):

        # Add vertex to inner vertex buffer
        self.__vertices.append(vertex)
        vertex_index = self.vertex_count

        # Check if we already have a node for the vertex
        node_index = self.__vertex_node_dict.get(tuple(vertex))

        if node_index is None: # There is no readily defined vertex -> node connection

            # Try to find a node that is close to our given vertex
            node_index, closest = self.find_closest_node(vertex)

            if not closest: # we could not find an existing node close enough

                # append a copy of the vertex as a new node to the node buffer
                self.__nodes.append(vertex[::])
                node_index = self.node_count - 1

                # update connection from node to vertex index
                self.__node_vertex_table.create_connection(node_index)
                self.__node_vertex_table.update_connection(node_index, vertex_index)

            else: # we do have a valid node close enough
                
                # add vertex connection to node table
                self.__node_vertex_table.read_connection(node_index).append(vertex_index)
            

        else: # we already have some node data defined for that vertex position

            # add vertex connection to node table
            self.__node_vertex_table.read_connection(node_index).append(vertex_index)


        # establish one-to-one connection from vertex to node index
        self.__vertex_node_dict[tuple(vertex)] = node_index

