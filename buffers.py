import math
import logging
import numpy as np

class OneToManyConnectionTable():
    """
    Convenience mapper Class to generate OneToMany Bindings.
    The class is backed by a dictionary and exposes a CRUD API for safe operations on it.
    """

    def __init__(self):
        # initialize empty backing dictionary
        self.__connections = {}

        # # TODO: We could generalize a backing keystore if we only ever allow ints as keys
        # # TODO: The collection can then only hand out valid indices
        # # initialize empty backing keystore <-?????
        # self.__keys = []

    def create_connection(self, key):
        """Create a new, empty connection

        Args:
            key (Any): The key for the connection
        """
        # initialize an empty list at the given key
        self.__connections[key] = []

        logging.debug("Created Connection for key: {}".format(key))

    def read_connection(self, key):
        """Reads the connection data for the given key

        Args:
            key (Any): The key for the connection

        Returns:
            List[Any]: A list of connected values, or None if the key is not found.
        """
        logging.debug("Read connection with key: {}".format(key))

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
        logging.debug("Delete connection for key {} and value {}".format(key, value))

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
        """
        All Values defined in the inner dict
        """
        return self.__connections.values()

    def items(self):
        """
        All items defined in the inner dict
        """
        return self.__connections.items()

    def keys(self):
        """
        All keys defined in the inner dict
        """
        return self.__connections.keys()

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
        """
        Initializes a new empty NodeBuffer
        """

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
        """
        Get all vertices in the buffer

        Returns:
            list[list[float]]: The vertices
        """
        # Copy the backing buffer, without the None entries
        return [vertex for vertex in self.__vertices.copy() if vertex is not None]

    def nodes(self):
        """Gives access to a copy of all unique nodes in the buffer.

        Returns:
            List[List[float]]: The nodes as lists of coordinates
        """
        # Copy the backing buffer, without the None entries
        return [node for node in self.__nodes.copy() if node is not None]

    def __next_available_node_index(self):
        return len(self.__nodes)

    def __next_available_vertex_index(self):
        return len(self.__vertices)

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
        for index in self.node_indices():
            node = self.__nodes[index]
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
            vertex (List[float]): The vertex to add.

        Returns:
            int: The index of the added vertex.
        """

        # Add vertex to inner vertex buffer
        vertex_index = self.__next_available_vertex_index()
        self.__vertices.append(vertex)

        # In the rare case that no nodes are defined at all, the next step is quite trivial
        if self.node_count == 0:
            # Append a copy of the vertex as a new node
            node_index = self.__next_available_node_index()
            self.__nodes.append(vertex.copy())

            # Link tables together
            self.__vertex_node_dict[vertex_index] = node_index
            self.__node_vertex_table.create_connection(node_index)
            self.__node_vertex_table.update_connection(node_index, vertex_index)

            logging.info("Added new vertex {} with index {} as it's own parent into empty node buffer at index {}".format(vertex, vertex_index, node_index))

            return vertex_index

        # Check if we already have a node for the vertex
        # TODO: This seems like a relic from when we used vertex coords to find node parents.
        node_index = self.__vertex_node_dict.get(vertex_index)

        if node_index is None: # There is no readily defined vertex -> node connection

            # Try to find a node that is close to our given vertex
            node_index, parent = self.find_parent_node(vertex)

            if parent is None: # we could not find an existing node close enough

                # append a copy of the vertex as a new node to the node buffer
                node_index = self.__next_available_node_index()
                self.__nodes.append(np.copy(vertex))

                # update connection from node to vertex index
                self.__node_vertex_table.create_connection(node_index)
                self.__node_vertex_table.update_connection(node_index, vertex_index)

                logging.info("Added new vertex {} with index {} as it's own parent into node buffer at index {}".format(vertex, vertex_index, node_index))

            else: # we do have a valid node close enough
                
                # DEBUG
                connection = self.__node_vertex_table.read_connection(node_index)
                if connection is None:
                    logging.warn("Could not read vertex connection for node_index {}, although the index was obtained from self.find_parent_node({})".format(node_index, vertex))

                    # self.__node_vertex_table.create_connection(node_index)

                # add vertex connection to node table
                self.__node_vertex_table.read_connection(node_index).append(vertex_index)
            
                logging.info("Added new vertex {} with index {} with parent node at index {}".format(vertex, vertex_index, node_index))

        else: # we already have some node data defined for that vertex position

            # DEBUG
            connection = self.__node_vertex_table.read_connection(node_index)
            if connection is None:
                logging.warn("Could not read vertex connection for node_index {}, although the index was obtained from self.__vertex_node_dict[{}]".format(node_index, vertex_index))

            # add vertex connection to node table
            self.__node_vertex_table.read_connection(node_index).append(vertex_index)

            logging.info("Added new vertex {} with index {} with parent node at index {}".format(vertex, vertex_index, node_index))

        # establish one-to-one connection from vertex to node index
        self.__vertex_node_dict[vertex_index] = node_index

        return vertex_index

    def get_vertex(self, index):
        """
        Gets the vertex for the given vertex index

        Args:
            index (int): The index of the vertex

        Returns:
            list[float]: The coordinates of the vertex
        """

        return self.__vertices[index]

    def get_parent_node(self, vertex_index):
        """
        Gets the parent node of the given vertex

        Args:
            vertex_index (int): The index of the vertex to get the parent of.

        Returns:
            int: The index of the parent node.
        """

        return self.__vertex_node_dict[vertex_index]

    def get_node_children(self, node_index):
        """
        Gets all the children vertex of the given node

        Args:
            node_index (int): The index of the node to find the children of

        Returns:
            list[int] | None: The indices of the vertices, or None on failure
        """

        return self.__node_vertex_table.read_connection(node_index)

    def remove_node(self, index):
        """
        Removes the given node from the buffer.
        Nodes can only be removed if all their children have been removed first.

        Args:
            index (int): The index of the node to remove
            
        Returns:
            bool: True if the node was removed, False if it was not.
        """

        # Read out node
        node = self.__nodes[index]

        if node is None: return False

        # Check if node is empty
        children = self.get_node_children(index)
        if len(children) != 0: return False

        # If the node is empty, it is safe to remove it
        self.__node_vertex_table.delete_connection(index)
        self.__nodes[index] = None

        logging.info("Successfully removed node {} from index {}".format(node, index))

        return True

    def remove_vertex(self, index):
        """
        Removes the given vertex from the buffer.

        Args:
            index (int): The index of the vertex to remove.

        Returns:
            bool: True if the vertex was removed, False if it was not.
        """

        # check for index out of range
        if index >= len(self.__vertices): return False

        # check if vertex is already removed
        vertex = self.get_vertex(index)
        if vertex is None: return False

        # Get the parent for the vertex
        node = self.get_parent_node(index)

        # Remove vertex from node connection
        self.__node_vertex_table.delete_connection(node, index)

        # Remove vertex from vertex table
        del self.__vertex_node_dict[index]

        # Set vertex to null in backing buffer
        self.__vertices[index] = None

        logging.info("Successfully removed vertex {} at index {}".format(vertex, index))

        # Try to also remove parent node, if it is now empty
        self.remove_node(node)


        return True

    def vertex_indices(self):
        """
        A list of all the vertex indices in the buffer

        Returns:
            list[int]: The indices of the verts
        """
        return [i for i in range(len(self.__vertices)) if self.__vertices[i] is not None]

    def node_indices(self):
        """
        A list of all the node indices in the buffer

        Returns:
            list[int]: The indices of the nodes
        """

        return [i for i in range(len(self.__nodes)) if self.__nodes[i] is not None]

    def is_topology_valid(self):
        """
        Test of the NodeBuffer has valid topology.
        The topology is considered valid if no nodes are without children
        and no vertices are without parents.
        Also the children of a node must all link back to it.

        Returns:
            bool: True if the topology is valid, False if it is not.
        """
        has_errors = False

        # Test all vertices are linked up to a parent node
        for index in self.vertex_indices():
            self.get_parent_node(index) # this will throw if no parent is linked

        # Test all nodes to have children
        for index in self.node_indices():
            children = self.get_node_children(index)
            if not children:
                print("Topology ERROR: Node %i has no children!", index)
                has_errors = True
            for child in children:
                parent_index = self.get_parent_node(child)
                if parent_index != index:
                    print("Topology ERROR: Node %i has a dangling reference to vertex %i, which references node %i", index, child, parent_index)
                    has_errors = True

        return not has_errors
