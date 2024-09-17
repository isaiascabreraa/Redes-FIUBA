
import signal
import sys
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel

def signal_handler(sig, frame):
        print("Cerrando red de Mininet")
        net.stop()
        sys.exit(0)

def udpNetwork():
    net = Mininet(controller=Controller)
    net.addController('c0')

    # Añade los hosts
    client = net.addHost('h1')
    server = net.addHost('h2')

    # Añade un switch
    s1 = net.addSwitch('s1')

    # Conecta los hosts al switch
    net.addLink(client, s1)
    net.addLink(server, s1)

    # Inicia la red
    net.start()

    # Ejecuta el servidor en h2
    server.cmd('python3 udp_server.py &')

    # Ejecuta el cliente en h1
    client.cmd('python3 udp_client.py &')

    signal.signal(signal.SIGINT, signal_handler)

    # Inicia la CLI de Mininet para interactuar con la red
    CLI(net)

    # Detiene la red
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    udpNetwork()

