from mesh import FEMMesh
import pickle
import pickletools
import argparse
import rhino_io
import json

CMD_POLYGON = "polygon"

SERIALIZATION_FILE = "data.pkl"

MESH_SINGLETON = FEMMesh()
"""
The one and only mesh instance that can exist inside the server,
at any given time
"""


def __deserialize_singleton():
    with open(SERIALIZATION_FILE, 'rb') as file:
        MESH_SINGLETON = pickle.load(file)


def __serialize_singleton():
    with open(SERIALIZATION_FILE, 'wb') as file:
        pickle.dump(MESH_SINGLETON, file, 3)


class Argument(object):
    def __init__(self, name, arg_type, default=None, help=""):
        self.name = name
        self.arg_type = arg_type
        self.default = default
        self.help = help

    def flag(self):
        return f"--{self.name}"

    def short_flag(self):
        return f"-{self.name[0]}"

    def __str__(self):
        return self.flag()


def arg_to_flag(arg, short=True):
    short_flag = f"-{arg[0]}"
    long_flag = f"--{arg}"

    if short:
        return short_flag
    else:
        return long_flag


def add_Arguments(parser, arguments):
    for arg in arguments:
        parser.add_argument(
            arg.short_flag(),
            arg.flag(),
            type=arg.arg_type,
            help=arg.help,
            default=arg.default,
        )


def main():
    # create parser and subparser
    parser = argparse.ArgumentParser(description="Run FEM commands on a mesh")
    subparsers = parser.add_subparsers(dest="cmd_name")

    # create a base subparser with global commands
    GLOBAL_SUBDIVIDE_ARGUMENT = Argument(
        "subdivide", int, help="Subdivide the mesh faces n times")
    GLOBAL_TRANSFER_ARGUMENT = Argument(
        "transfer", bool, help="Transfer the mesh as serialized bytes over stdout")
    base_subparser = argparse.ArgumentParser(add_help=False)
    add_Arguments(base_subparser, [
        GLOBAL_SUBDIVIDE_ARGUMENT, GLOBAL_TRANSFER_ARGUMENT])

    # add polygon command
    POLYGON_RADIUS_ARGUMENT = Argument(
        "radius", float, 1.0, "radius of polygon")
    POLYGON_SIDECOUNT_ARGUMENT = Argument(
        "n_sides", int, 4, "number of sides in the polygon"
    )
    poly_cmd = subparsers.add_parser(CMD_POLYGON, parents=[base_subparser])
    add_Arguments(poly_cmd, [POLYGON_RADIUS_ARGUMENT,
                  POLYGON_SIDECOUNT_ARGUMENT])

    # parse args
    args = parser.parse_args()

    # match on args subcommand
    if args.cmd_name == CMD_POLYGON:
        MESH_SINGLETON = FEMMesh.polygon(
            args.__getattribute__(POLYGON_RADIUS_ARGUMENT.name),
            args.__getattribute__(POLYGON_SIDECOUNT_ARGUMENT.name),
        )

    # match on global flags
    subd_level = args.__getattribute__(GLOBAL_SUBDIVIDE_ARGUMENT.name)
    if subd_level is not None:
        MESH_SINGLETON.subdivide_faces(subd_level)

    # match on retrieve flag
    transfer = args.__getattribute__(GLOBAL_TRANSFER_ARGUMENT.name)
    if transfer is not None:
        # write serialized mesh to stdout
        buffer = rhino_io.MeshBuffer(MESH_SINGLETON)
        dump = json.dumps((buffer.coords, buffer.faces))
        # dump = pickle.dumps(buffer.coords, protocol=2)
        print(dump)
        # print(pickle.dumps(rhino_io.MeshBuffer(MESH_SINGLETON), 2))
    else:
        # write serialized mesh to temp_file
        __serialize_singleton()
        print("success")


if __name__ == "__main__":
    main()
