import logging
import subprocess
import json
from subprocess import Popen, PIPE
import arguments


class Proxy(object):
    def __init__(self):
        self.__server_process = Popen(
            "python3 -u server.py", stdin=PIPE, stdout=PIPE, stderr=PIPE
        )

    def __send_cmd(self, cmd):
        cmd_bytes = "{}\n".format(cmd).encode("utf-8")
        self.__server_process.stdin.write(cmd_bytes)
        self.__server_process.stdin.flush()

    def subdivide(self, n_subd):
        cmd = CommandBuilder().subdivide(n_subd).build()
        self.__send_cmd(cmd)

    def polygon(self, radius=None, n_sides=None):
        cmd = CommandBuilder().polygon(radius, n_sides).build()
        self.__send_cmd(cmd)

    def receive(self):
        cmd = CommandBuilder().transfer().build()
        self.__send_cmd(cmd)

        result = json.loads(self.__server_process.stdout.readline())
        return (result[0], result[1])

    def close(self):
        cmd = CommandBuilder().quit().build()
        self.__send_cmd(cmd)
        print(self.__server_process.wait(timeout=1))


class CommandBuilder(object):
    def __init__(self):
        self.__transfer = None
        self.__subdivide = None
        self.__subcommand = arguments.CMD_NOOP

    def transfer(self):
        self.__transfer = True
        return self

    def subdivide(self, n_subd):
        self.__subdivide = n_subd
        return self

    def polygon(self, radius=None, n_sides=None):
        self.__subcommand = arguments.CMD_POLYGON
        if radius is not None:
            self.__subcommand += " {} {}".format(
                arguments.POLYGON_RADIUS_ARGUMENT.short_flag(), radius
            )
        if n_sides is not None:
            self.__subcommand += " {} {}".format(
                arguments.POLYGON_SIDECOUNT_ARGUMENT.short_flag(), n_sides
            )
        return self

    def house(self, depth=None):
        self.__subcommand = arguments.CMD_HOUSE
        if depth is not None:
            self.__subcommand += " {} {}".format(
                arguments.HOUSE_DEPTH_ARGUMENT.short_flag(), depth
            )
        return self

    def orient(self, face_index=None):
        self.__subcommand = arguments.CMD_ORIENT
        if face_index is not None:
            self.__subcommand += " {} {}".format(
                arguments.ORIENT_FACE_INDEX_ARGUMENT.short_flag(), face_index
            )
        return self

    def reset(self):
        self.__subcommand = arguments.CMD_RESET
        return self

    def quit(self):
        self.__subcommand = arguments.TOP_LEVEL_QUIT_ARGUMENT.short_flag()
        return self

    def __command_string(self):
        if self.__subcommand is None:
            return

        cmd = self.__subcommand

        if self.__subdivide is not None:
            cmd += " {} {}".format(
                arguments.GLOBAL_SUBDIVIDE_ARGUMENT.short_flag(), self.__subdivide
            )

        if self.__transfer is not None:
            cmd += " {}".format(arguments.GLOBAL_TRANSFER_ARGUMENT.short_flag())

        return cmd

    def build(self):
        return self.__command_string()


if __name__ == "__main__":
    proxy = Proxy()
    proxy.polygon()
    proxy.subdivide(1)
    print(proxy.receive())

    proxy.close()
