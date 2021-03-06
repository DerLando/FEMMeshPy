import unittest
from buffers import OneToManyConnectionTable, NodeBuffer
import logging
import numpy as np


class TestConnectionTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            filename="tests/test_output/tests.log",
            filemode="w",
            level=logging.INFO,
        )

    def test_create(self):

        logging.info("test_create")

        table = OneToManyConnectionTable()
        table.create_connection(1)
        table.update_connection(1, 12, 13, "Hi")
        self.assertEqual(
            [12, 13, "Hi"],
            list(table.read_connection(1)),
            "SHould be a list of things.",
        )

    def test_delete(self):

        logging.info("test_delete")

        table = OneToManyConnectionTable()
        table.create_connection(1)
        table.delete_connection(1)

        self.assertEqual(0, table.count, "Should be 0.")

        table.delete_connection("upsi")

        table.create_connection(5)

        self.assertEqual(1, table.count, "Should be 1.")

        table.update_connection(5, "hi", 12, 0, 5)

        table.delete_connection(5, 0)

        self.assertEqual(
            ["hi", 12, 5], list(table.read_connection(5)), "Should be [hi, 12]."
        )


class TestNodeBuffer(unittest.TestCase):
    def test_add_vertex(self):

        logging.info("test_add_vertex")

        buffer = NodeBuffer()
        buffer.add_vertex(np.array([0, 0, 0]))
        self.assertEqual(1, buffer.vertex_count, "Should be 1!")
        self.assertEqual(1, buffer.node_count, "Should be 1!")

        buffer.add_vertex(np.array([0, 0, 0.0001]))
        self.assertEqual(2, buffer.vertex_count, "Should be 2!")
        self.assertEqual(1, buffer.node_count, "Should be 1!")

        for i in range(4):
            buffer.add_vertex(np.array([1, 2, 3.0 + i / 1000]))

        self.assertEqual(6, buffer.vertex_count, "Should be 6!")
        self.assertEqual(2, buffer.node_count, "Should be 2!")

    def test_remove_vertex(self):

        logging.info("test_remove_vertex")

        buffer = NodeBuffer()
        index = buffer.add_vertex(np.array([0, 0, 0]))
        self.assertTrue(buffer.remove_vertex(index))

        self.assertEqual(0, buffer.vertex_count)
        self.assertEqual(0, buffer.node_count)

        indices = [
            buffer.add_vertex(np.array([1, 2, 3.0 + i / 1000])) for i in range(4)
        ]

        for index in indices:
            self.assertEqual(1, buffer.node_count)
            buffer.remove_vertex(index)

        self.assertEqual(0, buffer.vertex_count)
        self.assertEqual(0, buffer.node_count)


if __name__ == "__main__":

    logging.basicConfig(
        filename=".\\tests\\test_output\\test_buffers.log",
        filemode="w",
        level=logging.INFO,
    )
    unittest.main()
