# Grupo 6 - TP 1 File Transfer
## Integrantes

### Dependencias

    chmod +x ./bundle_install.sh
    ./bundle_install.sh

### Uso de Mininet

### Correr flake8
En la raiz correr:

    ./flake.sh
### Ejecucion de tests
En la raiz correr:

    ./run_tests.sh

## Interfaces

### Interfaz cliente
#### Upload

    > python upload -h
    usage: upload [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]

    <command description>

    optional arguments:
    -h, --help      show this help message and exit
    -v, --verbose   increase output verbosity
    -q, --quiet     decrease output verbosity
    -H, --host      server IP address
    -p, --port      server port
    -s, --src       source file path
    -n, --name      file name

#### Download

    > python download -h
    usage: download [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]

    <command description>

    optional arguments:
    -h, --help      show this help message and exit
    -v, --verbose   increase output verbosity
    -q, --quiet     decrease output verbosity
    -H, --host      server IP address
    -p, --port      server port
    -d, --dst       destination file path
    -n, --name      file name

### Interfaz servidor

    > python start-server -h
    usage: start-server [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH]

    <command description>

    optional arguments:
    -h, --help      show this help message and exit
    -v, --verbose   increase output verbosity
    -q, --quiet     decrease output verbosity
    -H, --host      service IP address
    -p, --port      service port
    -s, --storage  storage dir path