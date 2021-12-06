import logging
import pickle
import xmlrpclib
from subprocess import Popen, PIPE, STDOUT
import Rhino.Geometry as rg
import itertools


SERVER_NAMESPACE = "localhost"
SERVER_PORT = 9000
RHINO_IO_TEMP_FILENAME = "temp_proxy_io.3dm"


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in xrange(0, len(seq), size))


class Proxy(object):
    def __enter__(self):
        # the return value is passed to the 'as' param in a with block
        return self

    def __exit__(self, type, value, tb):
        logging.debug("Proxy shutdown")
        self.server_process.terminate()

    def __init__(self):

        # spawn the server thread
        self.__spawn_server_thread()

        # initialize the server proxy
        self.server_proxy = xmlrpclib.ServerProxy(
            "http://{}:{}".format(SERVER_NAMESPACE, SERVER_PORT)
        )

    def __spawn_server_thread(self):
        self.server_process = Popen(
            "python3 server.py", shell=True, stdout=PIPE, stderr=PIPE
        )

    @staticmethod
    def __mesh_from_buffer(buffer):
        mesh = rg.Mesh()
        for chunk in chunker(buffer.coords, 3):
            mesh.Vertices.Add(chunk[0], chunk[1], chunk[2])

        for face in buffer.faces:
            mesh.Faces.AddFace(next(face), next(face), next(face), next(face))

        return mesh

    @property
    def mesh(self):
        return self.server_proxy

    def get_mesh(self):
        bytes = self.mesh.retrieve()
        buffer = pickle.load(bytes)
        return self.__mesh_from_buffer(buffer)

    @staticmethod
    def convert_to_native(retrieved_mesh):
        """
        And this is where the dream dies.
        There is no way in Rhinocommon v6 to de-serialize the json object from rhino3dm.
        So I can create and manipulate the mesh on the server all fine, but in the end,
        we will need to go through file bound io.

        One last idea, write file3dm to clipboard and insert in rhino...
        """
        return rg.Mesh.FromJson(retrieved_mesh)


def main():

    retrieved = None

    with Proxy() as proxy:

        print(proxy.server_proxy.ping())
        # print(proxy.server_proxy.mesh.polygon(1, 4))

        print(proxy.mesh.add_face([[0, 0, 0], [1.0, 0, 0], [0.5, 1.0, 0.0]]))

        # try:
        #     print(proxy.mesh.retrieve())
        # except xmlrpclib.Error as e:
        #     print(e.faultString)

        retrieved = proxy.get_mesh()

        print("Success")

    print(retrieved)
    # mesh = Proxy.convert_to_native(retrieved)
    # print(mesh)


if __name__ == "__main__":
    main()
