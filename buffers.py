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
        """Calculates the number connections defined

        Returns:
            int: The number of connections
        """
        return len(self.__connections)

    def values(self):
        return self.__connections.values()

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
        # Internal dict matching one vertex index to one node_index
        self.__vertex_node_dict = {}

        # TODO: Indexing by vertex position is dangerous, as we might have multiple vertices at the same position

    @property
    def node_count(self):
        """Calculates the number of unique nodes stored in the buffer.

        Returns:
            int: The number of nodes.
        """
        return len(self.nodes())

    @property
    def vertex_count(self):
        """Calculates the number of unique vertices stored in the buffer.

        Returns:
            int: The number of vertices.
        """

        return len(self.vertices())

    def vertices(self):
        # Copy the backing buffer, without the None entries
        return [vertex for vertex in self.__vertices.copy() if vertex]

    def nodes(self):
        """Gives access to a copy of all unique nodes in the buffer.

        Returns:
            List[List[float]]: The nodes as lists of coordinates
        """
        # Copy the backing buffer, without the None entries
        return [node for node in self.__nodes.copy() if node]

    def __round_vertex(cls, vertex):
        """Rounds the coordinates of a given vertex to the inner equality precision

        Args:
            vertex (List[float]): the vertex coordinates as a list

        Returns:
            List[float]: the rounded coordinate values as a list
        """
        return [round(coord, cls.__NODE_ROUND_DIGITS) for coord in vertex]

    def __vertex_distance(cls, a, b):
        """Calculate the distance between two vertices

        Args:
            a (List[float]): The first vertex
            b (List[float]): The second vertex

        Returns:
            float: The calculated distance
        """
        return math.sqrt(sum([(c0 - c1)**2 for c0, c1 in zip(a, b)]))

    def find_parent_node(self, vertex):
        """Finds the parent node for a given vertex.
        The parent in this context is a node with a distance
        to the vertex that is smaller than cls.__NODE_EQUALITY_EPSILON

        Args:
            vertex (List[float]): the vertex coordinates as a list

        Returns:
            tuple[int, List[int]] | tuple[None, None]: The parent node with it's index, or None if no parent exists.
        """
        for index, node in enumerate(self.__nodes):
            if node is None: continue
            dist = self.__vertex_distance(node, vertex)
            if dist < self.__NODE_EQUALITY_EPSILON:
                return (index, node)

        return (None, None)

    # def find_closest_node(self, vertex):
    #     dist = float("inf")
    #     found = -1
    #     for index, node in enumerate(self.nodes()):
    #         cur_dist = self.__vertex_distance(node, vertex)
    #         if cur_dist < self.__NODE_EQUALITY_EPSILON:
    #             return (index, node)
    #         if cur_dist < dist:
    #             dist = cur_dist
    #             found = index

    #     if found == -1:
    #         return (None, None)

    #     return (found, self.__nodes[found])

    def add_vertex(self, vertex):
        """Adds the given vertex to the buffer.
        This will automatically add another node, too
        if no suitable parent node for the vertex is found.

        Args:
            vertex (List[int]): The vertex to add.
        """

        # Add vertex to inner vertex buffer
        vertex_index = len(self.__vertices)
        self.__vertices.append(vertex)

        # In the rare case that no nodes are defined at all, the next step is quite trivial
        if self.node_count == 0:
            # Append a copy of the vertex as a new node
            node_index = len(self.__nodes)
            self.__nodes.append(vertex.copy())

            # Link tables together
            self.__vertex_node_dict[vertex_index] = node_index
            self.__node_vertex_table.create_connection(node_index)
            self.__node_vertex_table.update_connection(node_index, vertex_index)

            return vertex_index

        # Check if we already have a node for the vertex
        node_index = self.__vertex_node_dict.get(vertex_index)

        if node_index is None: # There is no readily defined vertex -> node connection

            # Try to find a node that is close to our given vertex
            node_index, parent = self.find_parent_node(vertex)

            if not parent: # we could not find an existing node close enough

                # append a copy of the vertex as a new node to the node buffer
                node_index = self.node_count
                self.__nodes.append(vertex[::])

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
        self.__vertex_node_dict[vertex_index] = node_index

        return vertex_index

    def get_vertex(self, index):
        return self.__vertices[index]

    def get_parent_node(self, vertex_index):
        return self.__vertex_node_dict[vertex_index]

    def get_node_children(self, node_index):
        return self.__node_vertex_table.read_connection(node_index)

    def remove_node(self, index):
        # Read out node
        node = self.__nodes[index]

        if node is None: return False

        # Check if node is empty
        children = self.get_node_children(index)
        if len(children) != 0: return False

        # If the node is empty, it is safe to remove it
        self.__node_vertex_table.delete_connection(index)
        self.__nodes[index] = None

        return True

    def remove_vertex(self, index):
        # check for index out of range
        if index >= len(self.__vertices): return False

        # check if vertex is already removed
        if self.get_vertex(index) is None: return False

        # Get the parent for the vertex
        node = self.get_parent_node(index)

        # Remove vertex from node connection
        self.__node_vertex_table.delete_connection(node, index)

        # Remove vertex from vertex table
        del self.__vertex_node_dict[index]

        # Set vertex to null in backing buffer
        self.__vertices[index] = None

        # Try to also remove parent node, if it is now empty
        self.remove_node(node)

        return True



