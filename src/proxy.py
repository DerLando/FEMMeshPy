import logging
import subprocess
import json
from subprocess import Popen, PIPE
import arguments
import logging
import threading
import Queue
import time

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d - %H:%M:%S"
)
fh = logging.FileHandler("proxy.log", "w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)


def output_reader(proc, outq):
    for line in proc.stdout:
        outq.put(line)

    # works only in python3:
    # for line in iter(proc.stdout.readline, ''):
    #     outq.put(line)


class Proxy(object):
    def __init__(self):
        self.__server_process = Popen("python3 -u server.py", stdin=PIPE, stdout=PIPE)
        self.__line_queue = Queue.Queue()
        self.__reader_thread = threading.Thread(
            target=output_reader, args=(self.__server_process, self.__line_queue)
        )

        self.__reader_thread.start()

    def __send_cmd(self, cmd):
        log.debug("Send command: {}".format(cmd))
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

        return self.__parse_received()

    def execute_command(self, cmd):
        self.__send_cmd(cmd)

        if arguments.GLOBAL_TRANSFER_ARGUMENT.short_flag() in cmd:
            return self.__parse_received()

    def __parse_received(self):
        for _ in range(10):
            try:
                line = self.__line_queue.get(block=False)
                break
            except Queue.Empty:
                log.warning("Tried to parse empty line queue")
                time.sleep(0.2)
                continue
        log.debug("parse dump: {}".format(line))
        result = json.loads(line)
        return (result[0], result[1])

    def close(self):
        cmd = CommandBuilder().quit().build()
        self.__send_cmd(cmd)
        log.debug(
            "Server process exited with code {}".format(self.__server_process.wait())
        )


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
    for i in range(6):

        proxy.execute_command(CommandBuilder().house(10.0).build())
        cmd = CommandBuilder().orient(i).subdivide(1).transfer().build()
        proxy.execute_command(cmd)

    proxy.close()
