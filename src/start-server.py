import sys
import os
import socket
import threading
import time
import lib.utils as utils
from lib.utils import print_msg

from lib.StopAndWaitProtocol import StopAndWaitProtocol
from lib.SackProtocol import SackProtocol
from lib.packet_functions import get_seq_num, get_header_and_payload, get_protocol, get_msg_type

HELP_MENU = "-h"
BUF_SIZE = 2048
READ_SIZE = 2040
MIN_PORT = 1024
MAX_PORT = 65535
MAX_VALID_PARAMETERS = 5
NAME_END = "\n"

''' | Ack | Seq Num | Algoritmo | P Len |
    | 1B  |   4B    |    1B     |  2B   |
'''


def main():
    parser = utils.get_server_parser()
    args = parser.parse_args()

    utils.set_verbose(args, "server")

    args.storage = os.path.abspath(args.storage)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 5*1024*1024)
    server_socket.bind((args.host, args.port))

    print_msg("\nServer is ready.\n", "server")

    threads = []
    clients = {}

    closed = [False]
    protocol = None

    while not closed[0]:
        try:
            pkt, client_address = server_socket.recvfrom(BUF_SIZE)
            print_msg(f"LLEGO PAQUETE de {client_address}", "server")
            header, payload = get_header_and_payload(pkt)
            if client_address not in clients:
                protocol_type = get_protocol(pkt)
                if protocol_type == utils.RDTAlgo.SACK.value:
                    protocol = SackProtocol(server_socket, client_address, "server")
                else:
                    protocol = StopAndWaitProtocol(server_socket, client_address, "server")
                clients[client_address] = protocol
                protocol.put(pkt)
            else:
                clients[client_address].put(pkt)

            if get_seq_num(header) == 0 and not clients[client_address].first_packet_received:
                clients[client_address].first_packet_received = True

                msg_type = get_msg_type(header)

                if get_protocol(header) == 1:
                    file_name = clients[client_address].receive_first_pkt()
                else:
                    file_name = payload

                if msg_type == 0:
                    print_msg(f"Cliente descarga nuevo {client_address}", "server")
                    download = threading.Thread(target=download_server, args=(clients[client_address], file_name.decode(), args.storage))
                    threads.append(download)
                    download.start()
                    threads.append(download)
                if msg_type == 1:
                    print_msg(f"Cliente carga nuevo {client_address}", "server")
                    upload = threading.Thread(target=upload_server, args=(clients[client_address], file_name.decode(), args.storage))
                    threads.append(upload)
                    upload.start()
                    threads.append(upload)

        except KeyboardInterrupt:
            protocol.end()
            closed[0] = True
            if protocol is not None:
                protocol.send(b"EOF", 0)

    print_msg("Cerrando threads", "server")
    for thread in threads:
        thread.join()
        print_msg("Thread terminado", "server")
    print_msg("\nServer is closed.\n", "server")


def download_server(protocol, file_name, storage_path):
    firsttime = time.time()
    print_msg(f"Enviando el archivo: {file_name}", "server")
    try:
        with open(storage_path + "/" + file_name, 'rb') as f:
            buffer = f.read(READ_SIZE)
            while buffer:
                protocol.send(buffer, 0)
                buffer = f.read(READ_SIZE)
            protocol.send(b"EOF", 0)
            print_msg(f"archivo enviado {file_name}", "server")
    except FileNotFoundError:
        print(f"Error: El archivo '{file_name}' no existe.", file=sys.stderr)
        protocol.send(b"EOF", 0)
    endtime = time.time()
    print_msg(f"Termino escribir archivo: {file_name}", "server")
    print_msg(f"Tardó {endtime - firsttime} segundos", "server")


def upload_server(protocol, file_name, storage_path):
    firsttime = time.time()
    print_msg(f"Recibiendo el archivo: {file_name}", "server")
    protocol.receive()  # Porque el primer receive es el nombre del archivo, estuve como una hora por esto
    with open(storage_path + "/" + file_name, 'wb') as file:
        while True:
            buffer = protocol.receive()
            if buffer == b"EOF":
                break
            else:
                file.write(buffer)
    endtime = time.time()
    protocol.end()
    print_msg(f"Termino escribir archivo: {file_name}", "server")
    print_msg(f"Tardó {endtime - firsttime} segundos", "server")


if __name__ == "__main__":
    main()
