
import socket
import signal
import sys

def udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('10.0.0.2', 12457)  # Dirección IP del servidor

    def signal_handler(sig, frame):
        print("Cerrando cliente UDP")
        client_socket.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("Presiona 'q' para salir")
    while True:
        message = input("Introduce el mensaje: ")
        client_socket.sendto(message.encode(), server_address)
        if message == 'q':
            print("Cerrando cliente UDP")
            break

    client_socket.close()

if __name__ == "__main__":
    udp_client()
