import logging
import subprocess
import json


class Command(object):
    def execute(self):
        if self.cmd_string is None:
            return False

        output = subprocess.check_output(self.cmd_string)
        if output:
            result = json.loads(output)
            return (result[0], result[1])


class CommandBuilder(object):
    def __init__(self):
        self.__command = "python3 server.py"
        self.__transfer = None
        self.__subdivide = None
        self.__subcommand = None

    def transfer(self):
        self.__transfer = True
        return self

    def subdivide(self, n_subd):
        self.__subdivide = n_subd
        return self

    def polygon(self, radius=None, n_sides=None):
        self.__subcommand = "polygon"
        if radius is not None:
            self.__subcommand += " -r {}".format(radius)
        if n_sides is not None:
            self.__subcommand += " -n {}".format(n_sides)
        return self

    def house(self, depth=None):
        self.__subcommand = "house"
        if depth is not None:
            self.__subcommand += " -d {}".format(depth)
        return self

    def __command_string(self):
        if self.__subcommand is None:
            return

        cmd = self.__command
        cmd += " {}".format(self.__subcommand)

        if self.__subdivide is not None:
            cmd += " -s {}".format(self.__subdivide)

        if self.__transfer is not None:
            cmd += " -t {}".format(self.__transfer)

        return cmd

    def build(self):
        cmd = Command()
        cmd.cmd_string = self.__command_string()
        return cmd


if __name__ == "__main__":
    cmd = CommandBuilder().house(8).subdivide(2).transfer().build()
    print(cmd)
    print(cmd.execute())
