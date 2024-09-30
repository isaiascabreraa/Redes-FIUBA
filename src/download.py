import socket
import threading
import lib.utils as utils
import os
from lib.utils import print_msg

from lib.StopAndWaitProtocol import StopAndWaitProtocol
from lib.SackProtocol import SackProtocol

HELP_MENU = "-h"

MIN_PORT = 1024
MAX_PORT = 65535
MAX_VALID_PARAMETERS = 6
NAME_END = b"\n"
READ_SIZE = 2040
BUF_SIZE = 2048


def main():
    parser = utils.get_client_parser("download")
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

    file_path = args.dir_path + '/' + args.file_name

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if args.protocol == utils.RDTAlgo.SW.value:
        protocol = StopAndWaitProtocol(client_socket, (args.host, args.port), "client")
    elif args.protocol == utils.RDTAlgo.SACK.value:
        protocol = SackProtocol(client_socket, (args.host, args.port), "client")
    else:
        print("Select a protocol number between 0: Stop and Wait, 1: SACK")
        return

    protocol.send(args.file_name.encode(), 0)
    print_msg("Enviando", "client")

    closed = [False]

    thread = threading.Thread(target=write_file, args=(file_path, protocol, args.protocol))
    thread.start()

    while not closed[0]:
        try:
            pkt, address = client_socket.recvfrom(BUF_SIZE)
            print_msg(f"Recibiendo paquete de {address}", "client")
            protocol.put(pkt)
        except KeyboardInterrupt:
            closed[0] = True

    protocol.end()
    thread.join()
    print("Saliendo\n")


def write_file(file_name, protocol, protocol_type):
    with open(file_name, 'w+b') as file:
        if protocol_type == 1:
            buffer = protocol.receive_first_pkt()
            file.write(buffer)
        while True:
            buffer = protocol.receive()
            if buffer == b"EOF":
                break
            else:
                file.write(buffer)
    print_msg("Termino escribir archivo {file_name}", "client")


if __name__ == "__main__":
    main()
