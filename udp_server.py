
import socket
import signal
import sys

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 12457))
    print("Servidor UDP listo para recibir mensajes")

    def signal_handler(sig, frame):
        print("Cerrando servidor UDP")
        server_socket.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        data, addr = server_socket.recvfrom(1024)
        message = data.decode()
        print(f"Mensaje recibido de {addr}: {message}")
        if message == 'q':
            print("Cerrando servidor UDP")
            break

    server_socket.close()

if __name__ == "__main__":
    udp_server()
