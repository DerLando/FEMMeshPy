import subprocess
from xmlrpc.server import SimpleXMLRPCServer
import logging
import numpy as np
import rhino3dm

from mesh import FEMMesh

from rhino_io import RhinoIO

SERVER_NAMESPACE = "localhost"
SERVER_PORT = 9000
RHINO_IO_TEMP_FILENAME = "temp_proxy_io.3dm"

MESH_SINGLETON = FEMMesh()


class MeshProxy(object):
    @staticmethod
    def add_face(vertices):
        logging.debug(f"add_face({vertices})")
        if not isinstance(vertices, list):
            return -1
        return MESH_SINGLETON.add_face(np.array([np.array(v) for v in vertices]))

    @staticmethod
    def retrieve():
        logging.debug("retrieve")
        # file3dm = rhino3dm.File3dm()
        # file3dm.Objects.AddMesh(RhinoIO.convert_to_rhino(MESH_SINGLETON))

        return RhinoIO.convert_to_bytes(MESH_SINGLETON)


# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="server.log",
    filemode="w",
)

server = SimpleXMLRPCServer((SERVER_NAMESPACE, SERVER_PORT), logRequests=True)
server.register_introspection_functions()

server.register_instance(MeshProxy)


def ping():
    logging.debug("ping")
    return 1


server.register_function(ping)

try:
    print("Use Control-C to exit")
    server.serve_forever()
except KeyboardInterrupt:
    print("Exiting")
