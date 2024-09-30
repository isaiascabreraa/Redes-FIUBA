import queue
import threading
from lib.utils import print_msg

import lib.packet_functions as pf


class PacketSender:
    def __init__(self, pkt, timeout, address, skt, role):
        self.role = role
        self.pkt = pkt
        self.send_again = True
        self.timeout_event = threading.Event()
        self.timeout = timeout
        self.address = address
        self.socket = skt
        self.lock = threading.Lock()

    def send_pkt(self):
        while self.send_again:
            while not self.timeout_event.wait(self.timeout):  # Si el ACK no llega a tiempo el evento tira timeout y se vuelve a mandar el paquete
                try:
                    self.socket.sendto(self.pkt, self.address)
                except TimeoutError:
                    None
                print_msg("Intento timeout mandado", self.role)
            self.timeout_event.clear()  # Reseteo el evento

            with self.lock:
                if self.send_again:  # Si no ocurrio un timeout y el resend es true se vuelve a mandar el paquete
                    try:
                        self.socket.sendto(self.pkt, self.address)
                    except TimeoutError:
                        None

    def resend(self):
        self.timeout_event.set()

    def ack_arrived(self):
        with self.lock:
            self.send_again = False
            self.timeout_event.set()


class Window:
    def __init__(self, address, timeout, skt, role):
        self.role = role
        self.socket = skt
        self.time_out = timeout
        self.address = address
        self.packet_sender = {}
        self.max_size = 20
        self.pkt_sending = 0
        self.sending_num_lock = threading.Lock()
        self.window_lock = threading.RLock()
        self.window_full = threading.Condition()

    def end(self):
        with self.window_lock:
            for sqn_number in list(self.packet_sender.keys()):
                self.arrived(sqn_number)

    def send(self, pkt, sqn_number):
        with self.window_full:
            with self.sending_num_lock:
                condition = self.pkt_sending == self.max_size
            if condition:
                self.window_full.wait()
        sender = PacketSender(pkt, self.time_out, self.address, self.socket, self.role)
        with self.window_lock:
            self.packet_sender[sqn_number] = sender
        threading.Thread(target=sender.send_pkt, args=()).start()
        with self.sending_num_lock:
            self.pkt_sending += 1

    def resend(self, sqn_number):
        with self.window_lock:
            print_msg(f"Estos son los senders: {self.packet_sender}", self.role)
            pkt = self.packet_sender.get(sqn_number)
            pkt.resend()

    def arrived(self, sqn_number):
        with self.window_lock:
            self.packet_sender[sqn_number].ack_arrived()
            self.packet_sender.pop(sqn_number)
        with self.sending_num_lock:
            pkt_num = self.pkt_sending
            self.pkt_sending -= 1
        if pkt_num == self.max_size:
            with self.window_full:
                self.window_full.notify_all()


class SackProtocol:
    def __init__(self, skt, address, role):

        self.role = role

        self.first_packet_received = False

        self.window = Window(address, 0.1, skt, role)
        self.seq_num_sent = 0
        self.seq_num_act = 0
        self.receiver_num_seq_expected = 0

        self.packets = []
        self.packet_list_lock = threading.Lock()

        self.socket = skt
        self.address = address

        self.timeout = 0.08
        self.close_event = threading.Event()

        self.sender_queue = queue.Queue()
        self.receiver_queue = queue.Queue()
        self.receiver_return_queue = queue.Queue()
        self.first_packet_queue = queue.Queue()

        self.receiver = threading.Thread(target=self.receive_pkt, args=())
        self.sender = threading.Thread(target=self.send_window, args=())
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
        # print("Poniendo paquete en cola de receiver")
        self.receiver_queue.put(pkt)

    def send(self, payload, msg_type):
        pkt = pf.create_segment(msg_type, self.seq_num_act, 1, len(payload), payload)
        self.seq_num_act += len(payload)
        self.sender_queue.put(pkt)

    def receive_first_pkt(self):
        return self.first_packet_queue.get()

    def receive(self):
        return self.receiver_return_queue.get()
    

    def handle_sack(self, pkts_list):

            packet_received = False
            for pkt in pkts_list:
                header, payload = pf.get_header_and_payload(pkt)
                if pf.is_ack(header):

                    arrived_list = []
                    with self.window.window_lock:
                        seq_number_sended = list(self.window.packet_sender.keys())
                        for seq_number in seq_number_sended:
                            if seq_number < pf.get_seq_num(header):
                                arrived_list.append(seq_number)

                    seq_numbers = pf.get_sacks(payload)
                    for seq_number in seq_numbers:
                        if seq_number in seq_number_sended and seq_number not in arrived_list:
                            arrived_list.append(seq_number)
                            print_msg(f"Llego ACK de {seq_number}", self.role)

                    for seq_number in arrived_list:
                        self.window.arrived(seq_number)

                    with self.window.window_lock:
                        seq_number_sended = list(self.window.packet_sender.keys())
                    print_msg(f"Recibo Ack {pf.get_seq_num(header)} y Sacks {seq_numbers}", self.role)
                    print_msg(f"Enviando: {seq_number_sended}", self.role)
                    for seq_number in seq_number_sended:
                        if seq_number not in seq_numbers and len(seq_numbers) > 0 and seq_number < seq_numbers[-1]:
                            print_msg(f"Reenviando paquete: {seq_number}", self.role)
                            self.window.resend(seq_number)

                else:
                    print_msg("Contestando paquete", self.role)
                    if pf.get_seq_num(header) not in self.packets:
                        print_msg(f"Recibiendo paquete {pf.get_seq_num(header)}", self.role)
                        packet_received = True
                        self.packets.append((pf.get_seq_num(header), payload))

                return packet_received
            
    def handle_packet_received(self):
        self.packets = sorted(self.packets, key=lambda x: x[0])
        payload = bytearray()
        for pkt in self.packets:
            if pkt[0] == self.receiver_num_seq_expected:
                print_msg(f"Receiver seq num expected: {self.receiver_num_seq_expected}", self.role)
                print_msg(f"Seq_number_expected: {self.receiver_num_seq_expected}", self.role)
                if self.receiver_num_seq_expected == 0:
                    print_msg("Recibo primer paquete", self.role)
                    self.first_packet_queue.put(pkt[1])
                else:
                    if pkt[1] == b'EOF':
                        self.receiver_return_queue.put(payload)
                        self.receiver_return_queue.put(pkt[1])
                    else:
                        payload += pkt[1]
                self.receiver_num_seq_expected += len(pkt[1])

        self.receiver_return_queue.put(payload)

        seq_num_list = []
        for pkt in self.packets:
            if pkt[0] > self.receiver_num_seq_expected:
                print_msg(f"Creando sack porque {pkt[0]} > {self.receiver_num_seq_expected}", self.role)
                seq_num_list.append(pkt)
        self.packets = seq_num_list

        sacks = bytearray()
        for pkt in self.packets:
            sacks += pkt[0].to_bytes(4, byteorder='big')

        print_msg(f"Enviando ack {self.receiver_num_seq_expected} con sacks {sacks}", self.role)
        self.socket.sendto(pf.create_segment(2, self.receiver_num_seq_expected, 1, len(sacks), sacks), self.address)  # Mando ACK

    def receive_pkt(self):
        closed = False
        while not closed:
            pkts_list = []
            while not self.receiver_queue.empty():
                pkt = self.receiver_queue.get()
                if pkt is None:
                    closed = True
                else:
                    pkts_list.append(pkt)

            packet_received = self.handle_sack(pkts_list)

            if packet_received:
                self.handle_packet_received()
                
        self.window.end()
        print_msg("Saliendo de la window", self.role)

    def send_window(self):
        closed = False
        while not closed:
            pkt = self.sender_queue.get()
            if pkt is None:
                closed = True
            else:
                header, payload = pf.get_header_and_payload(pkt)
                print_msg("Enviando paquete", self.role)
                self.window.send(pkt, pf.get_seq_num(header))
