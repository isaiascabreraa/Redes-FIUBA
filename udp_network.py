from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel

def udpNetwork():
    net = Mininet(controller=Controller)
    net.addController('c0')

    # Añadir hosts
    client = net.addHost('h1')
    server = net.addHost('h2')

    # Añadir switch
    s1 = net.addSwitch('s1')

    # Conectar hosts al switch
    net.addLink(client, s1)
    net.addLink(server, s1)

    # Iniciar la red
    net.start()

    # Ejecutar el servidor en h2
    server.cmd('python3 udp_server.py &')

    # Ejecutar el cliente en h1
    client.cmd('python3 udp_client.py')

    # Iniciar la CLI de Mininet para interactuar con la red
    CLI(net)

    # Detener la red
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    udpNetwork()
