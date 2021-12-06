from mesh import FEMMesh
import pickle
import argparse
import rhino_io
import json
import task
from transform import transform_to_worldxy
import arguments
import logging
import logging.config
import sys

# logging.config.dictConfig(
#     {
#         "version": 1,
#         "disable_existing_loggers": True,
#     }
# )

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d - %H:%M:%S"
)
fh = logging.FileHandler("server.log", "w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)

MESH_SINGLETON = FEMMesh()
"""
The one and only mesh instance that can exist inside the server,
at any given time
"""


def add_arguments(parser, arguments):
    for arg in arguments:
        parser.add_argument(
            arg.short_flag(),
            arg.flag(),
            type=arg.arg_type,
            help=arg.help,
            default=arg.default,
        )


# create parser and subparser
parser = argparse.ArgumentParser(description="Run FEM commands on a mesh")
subparsers = parser.add_subparsers(dest="cmd_name")

# create a quit command to break inner loop
parser.add_argument("--quit", "-q", action="store_true", help="Quits the program")

# create a base subparser with global commands
base_subparser = argparse.ArgumentParser(add_help=False)
add_arguments(base_subparser, [arguments.GLOBAL_SUBDIVIDE_ARGUMENT])
base_subparser.add_argument(
    arguments.GLOBAL_TRANSFER_ARGUMENT.flag(),
    arguments.GLOBAL_TRANSFER_ARGUMENT.short_flag(),
    help=arguments.GLOBAL_TRANSFER_ARGUMENT.help,
    action="store_true",
)

# add polygon command
poly_cmd = subparsers.add_parser(arguments.CMD_POLYGON, parents=[base_subparser])
add_arguments(
    poly_cmd, [arguments.POLYGON_RADIUS_ARGUMENT, arguments.POLYGON_SIDECOUNT_ARGUMENT]
)

# add house command
house_cmd = subparsers.add_parser(arguments.CMD_HOUSE, parents=[base_subparser])
add_arguments(house_cmd, [arguments.HOUSE_DEPTH_ARGUMENT])

# add orient command
orient_cmd = subparsers.add_parser(arguments.CMD_ORIENT, parents=[base_subparser])
add_arguments(orient_cmd, [arguments.ORIENT_FACE_INDEX_ARGUMENT])

# add reset command
reset_cmd = subparsers.add_parser(arguments.CMD_RESET, parents=[base_subparser])

# add fall-through command
noop_cmd = subparsers.add_parser(arguments.CMD_NOOP, parents=[base_subparser])

while True:

    # get raw input
    astr = input()

    # parse args from raw input
    try:
        args = parser.parse_args(astr.split())
    except SystemExit:
        log.warning("Failed to parse raw input")
        continue

    # check if quit was called, early break
    if args.quit:
        log.debug("Quitting Server")
        break

    # match on args subcommand
    # create a polygon
    if args.cmd_name == arguments.CMD_POLYGON:
        log.debug(
            f"polygon, radius={args.__getattribute__(arguments.POLYGON_RADIUS_ARGUMENT.name)}, n_sides={args.__getattribute__(arguments.POLYGON_SIDECOUNT_ARGUMENT.name)}"
        )
        MESH_SINGLETON = FEMMesh.polygon(
            args.__getattribute__(arguments.POLYGON_RADIUS_ARGUMENT.name),
            args.__getattribute__(arguments.POLYGON_SIDECOUNT_ARGUMENT.name),
        )

    # create a house
    elif args.cmd_name == arguments.CMD_HOUSE:
        MESH_SINGLETON = task.House(
            task.COORDINATES_FRONT_FACE,
            args.__getattribute__(arguments.HOUSE_DEPTH_ARGUMENT.name),
        ).mesh

    # orient the mesh singleton on the given face
    elif args.cmd_name == arguments.CMD_ORIENT:
        plane = MESH_SINGLETON.get_face_plane(
            args.__getattribute__(arguments.ORIENT_FACE_INDEX_ARGUMENT.name)
        )
        MESH_SINGLETON.transform(transform_to_worldxy(plane))

    # reset the mesh singleton
    elif args.cmd_name == arguments.CMD_RESET:
        MESH_SINGLETON = FEMMesh()

    # match on global flags
    # face subdivision
    subd_level = args.__getattribute__(arguments.GLOBAL_SUBDIVIDE_ARGUMENT.name)
    if subd_level is not None:
        MESH_SINGLETON.subdivide_faces(subd_level)

    # retrieve mesh as json data
    transfer = args.__getattribute__(arguments.GLOBAL_TRANSFER_ARGUMENT.name)
    if transfer:
        # write serialized mesh to stdout
        log.debug("Transfer mesh singleton")
        buffer = rhino_io.MeshBuffer(MESH_SINGLETON)
        dump = json.dumps((buffer.coords, buffer.faces))
        sys.stdout.write(dump)
        sys.stdout.write("\n")
        sys.stdout.flush()
