#!/bin/bash

sudo apt install python3.10 python3-pip flake8 mininet python-is-python3 -y --fix-missing

# configuracion inicial python para valgrind
# sudo apt install pkg-config openssl -y
# REPO_FOLDER=$PWD
# PYTHON_VERSION="3.12.3"
# PYTHON_VER_FOLDER="3.12"
# PYTHON_ALT_FOLDER="/misc/alt2/python$PYTHON_VER_FOLDER"
# PYTHON_ALT_EXE="$PYTHON_ALT_FOLDER/bin/python$PYTHON_VER_FOLDER"
# cd misc

# wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
# tar -xvf Python-$PYTHON_VERSION.tgz
# cd Python-$PYTHON_VERSION

# configuracion de python
# ./configure --with-valgrind --enable-optimizations --prefix=$PYTHON_ALT_FOLDER

# instalacion de python personalizado en el sistema
# sudo make
# sudo make install
