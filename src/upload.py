import sys
import socket
import threading
import lib.utils as utils
from lib.utils import print_msg
import os

from lib.StopAndWaitProtocol import StopAndWaitProtocol
from lib.SackProtocol import SackProtocol

HELP_MENU = "-h"

MIN_PORT = 1024
MAX_PORT = 65535
MAX_VALID_PARAMETERS = 6
NAME_END = b"\n"
BUF_SIZE = 2048
READ_SIZE = 2040


def main():
    parser = utils.get_client_parser("upload")
    args = parser.parse_args()

    utils.set_verbose(args, "client")

    # validations
    if MIN_PORT > int(args.port) or int(args.port) >= MAX_PORT:
        print(f"Error: The allowed port range id (1024 - 65535), given {args.port}")
        return

    if not utils.path_exists(args.dir_path):
        print(f"Error: The path: '{args.dir_path}' not exists or is not a directory")
        return

    args.dir_path = os.path.abspath(args.dir_path)

    if utils.get_absolute_file_path(args.dir_path, args.file_name) is None:
        print(f"Error: The file '{args.file_name}' does not exist in '{args.dir_path}'", file=sys.stderr)
        return

    file_path = args.dir_path + '/' + args.file_name

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if args.protocol == utils.RDTAlgo.SW.value:
        protocol = StopAndWaitProtocol(client_socket, (args.host, args.port), "client")
    elif args.protocol == utils.RDTAlgo.SACK.value:
        protocol = SackProtocol(client_socket, (args.host, args.port), "client")
    else:
        print("Select a protocol number between 0: Stop and Wait, 1: SACK")
        return

    protocol.send(args.file_name.encode(), 1)
    closed = [False]

    reader = threading.Thread(target=read_file, args=(file_path, protocol))
    reader.start()

    while not closed[0]:
        try:
            pkt, address = client_socket.recvfrom(BUF_SIZE)
            print_msg(f"Recibiendo paquete de {address}", "client")
            protocol.put(pkt)
        except KeyboardInterrupt:
            closed[0] = True

    protocol.end()
    reader.join()


def read_file(file_path, protocol):
    try:
        with open(file_path, 'rb') as f:
            buffer = f.read(READ_SIZE)
            while buffer:
                protocol.send(buffer, 1)
                buffer = f.read(READ_SIZE)
            protocol.send(b"EOF", 1)
            print_msg(f"Archivo enviado {file_path}", "client")
    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no existe.", file=sys.stderr)
        protocol.send(b"EOF", 1)


if __name__ == "__main__":
    main()
