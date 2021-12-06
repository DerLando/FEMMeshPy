CMD_POLYGON = "polygon"
CMD_HOUSE = "house"
CMD_ORIENT = "orient"
CMD_RESET = "reset"
CMD_NOOP = "noop"


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


GLOBAL_SUBDIVIDE_ARGUMENT = Argument(
    "subdivide", int, help="Subdivide the mesh faces n times"
)
GLOBAL_TRANSFER_ARGUMENT = Argument(
    "transfer", bool, help="Transfer the mesh as serialized bytes over stdout"
)
TOP_LEVEL_QUIT_ARGUMENT = Argument("quit", bool, help="Quit the program")
POLYGON_RADIUS_ARGUMENT = Argument("radius", float, 1.0, "radius of polygon")
POLYGON_SIDECOUNT_ARGUMENT = Argument(
    "n_sides", int, 4, "number of sides in the polygon"
)
HOUSE_DEPTH_ARGUMENT = Argument("depth", float, 4.0, "depth of the generated house")
ORIENT_FACE_INDEX_ARGUMENT = Argument("index", int, 0, "face index to orient by")
