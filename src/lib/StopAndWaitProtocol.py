import threading
import queue
from lib.utils import print_msg

import lib.packet_functions as pf


class StopAndWaitProtocol:
    def __init__(self, skt, address, role):
        self.role = role
        self.first_packet_received = False

        self.seq_num_sent = 0
        self.seq_num_act = 0
        self.last_seq_num_received = 2  # Puse 2 para que no sea ni 0 ni 1

        self.socket = skt
        self.address = address

        self.timeout = 0.08
        self.timeout_event = threading.Event()

        self.sender_queue = queue.Queue()
        self.receiver_queue = queue.Queue()
        self.receiver_return_queue = queue.Queue()

        self.receiver = threading.Thread(target=self.receive_pkt, args=())
        self.sender = threading.Thread(target=self.send_pkt, args=())
        self.receiver.start()
        self.sender.start()

    def end(self):
        self.receiver_queue.put(None)
        self.sender_queue.put(None)
        print_msg("Cerrando receiver", self.role)
        self.receiver.join()
        print_msg("Cerrando sender", self.role)
        self.sender.join()

    def put(self, pkt):
        self.receiver_queue.put(pkt)

    def send(self, payload, msg_type):
        pkt = pf.create_segment(msg_type, self.seq_num_act, 0, len(payload), payload)
        if self.seq_num_act == 0: 
            self.seq_num_act = 1
        else:
            self.seq_num_act = 0
        self.sender_queue.put(pkt)

    def receive(self):
        return self.receiver_return_queue.get()

    def receive_pkt(self):

        while True:
            pkt = self.receiver_queue.get()
            if pkt is None:
                print_msg("pkt none en receive_pkt", self.role)
                break

            header, payload = pf.get_header_and_payload(pkt)
            if pf.is_ack(header):
                if pf.get_seq_num(header) == self.seq_num_sent:
                    print_msg(f"Llego ACK de {self.seq_num_sent}", self.role)
                    self.timeout_event.set()
            else:
                print_msg("Contestando paquete", self.role)
                self.socket.sendto(pf.create_segment(2, pf.get_seq_num(header), 0, 0, None), self.address)  # Mando ACK
                if pf.get_seq_num(header) != self.last_seq_num_received:  # Si no es un paquete repetido
                    self.receiver_return_queue.put(payload)
                    self.last_seq_num_received = pf.get_seq_num(header)

    def send_pkt(self):
        while True:
            pkt = self.sender_queue.get()
            if pkt is None:
                print_msg("pkt none en send_pkt", self.role)
                break
            print_msg(f"Enviando paquete {self.seq_num_sent}", self.role)
            self.socket.sendto(pkt, self.address)

            print_msg(f"Primer intento mandado {self.seq_num_sent}", self.role)
            while not self.timeout_event.wait(self.timeout):  # Si el ACK no llega a tiempo el evento tira timeout y se vuelve a mandar el paquete
                self.socket.sendto(pkt, self.address)
                print_msg(f"Intento timeout mandado {self.seq_num_sent}", self.role)
            self.timeout_event.clear()  # Reseteo el evento
            print_msg(f"Paquete {self.seq_num_sent} enviado \n", self.role)
            if self.seq_num_sent == 0:  # Cambio el sequence number, al solo poder mandar un paquete con un 0 y un 1 alcanza para diferenciarlos
                self.seq_num_sent = 1
            else:
                self.seq_num_sent = 0
