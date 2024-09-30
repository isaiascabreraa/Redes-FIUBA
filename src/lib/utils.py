import os
from enum import Enum
import argparse


class RDTAlgo(Enum):
    SW = 0
    SACK = 1


is_client_verbose = False
is_server_verbose = False


def get_client_parser(command_type):
    # Devuelve un parser de la API del lado del cliente
    parser = argparse.ArgumentParser(
        usage=f"{command_type} [-h] [-v | -q] [-H ADDR] [-p PORT] [-{'d' if command_type == 'download' else 's'} FILEPATH] [-n FILENAME]",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument("-q", "--quiet", action="store_true", help="decrease output verbosity")
    parser.add_argument("-H", "--host", type=str, required=False, default="localhost", help="server IP address")
    parser.add_argument("-p", "--port", type=int, required=False, default=10000, help="server port")
    parser.add_argument("-d" if command_type == "download" else "-s",
                        "--dst" if command_type == "download" else "--src",
                        type=lambda p: os.path.abspath(p),
                        default=os.path.abspath("./downloaded_files") if command_type == "upload" else os.path.abspath("./server_files"),
                        dest='dir_path',
                        help="destination file path" if command_type == "download" else "source file path")
    parser.add_argument("-n", "--name", type=str, required=True, dest='file_name', help="file name")
    parser.add_argument("-P", "--protocol", type=int, required=False, default=0,
                        help="chooses over which RDT protocol to comunicate with the server, 0 is Stop & Wait and 1 is SACK")

    return parser


def get_server_parser():
    # Devuelve un parser de la API del lado del servidor
    parser = argparse.ArgumentParser(
        usage="start-server [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH]",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument("-q", "--quiet", action="store_true", help="decrease output verbosity")
    parser.add_argument("-H", "--host", type=str, required=False, default='localhost', help="service IP address")
    parser.add_argument("-p", "--port", type=int, required=False, default=10000, help="service port")
    parser.add_argument("-s", "--storage", type=lambda p: os.path.abspath(p), required=False,
                        default=os.path.abspath("./server_files"), help="storage directory path")
    return parser


def set_verbose(args, role):
    global is_client_verbose, is_server_verbose
    if role == "client":
        if args.quiet:
            is_client_verbose = False
        elif args.verbose:
            is_client_verbose = True
        else:
            is_client_verbose = False
    if role == "server":
        if args.quiet:
            is_server_verbose = False
        elif args.verbose:
            is_server_verbose = True
        else:
            is_server_verbose = False


def path_exists(path):
    # Verifica si la path existe y si es un directorio
    absolute_path = os.path.abspath(path)
    return os.path.exists(absolute_path) and os.path.isdir(absolute_path)


def get_absolute_file_path(directory, file_name):
    for file in os.listdir(directory):
        if file == file_name:
            return os.path.join(directory, file)  # Devuelve la ruta completa
    return None


def print_msg(msg, role):
    if role not in ["client", "server"]:
        return
    if role == "server" and not is_server_verbose:
        return
    if role == "client" and not is_client_verbose:
        return
    print(msg)
