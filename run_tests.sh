#!/bin/bash

#colors
RED='\033[0;31m'
GREEN='\033[0;32m'
AMARILLO='\033[0;33m'
NC='\033[0m' # No Color 

#valgrind
#--show-reachable=yes --trace-children=yes --track-fds=yes --track-origins=no --time-stamp=yes
VALGRIND_FLAGS="valgrind --tool=memcheck --suppressions=misc/valgrind-python.supp"

PYTHON_VER_FOLDER="3.12"
PYTHON_ALT_FOLDER="/misc/alt2/python-$PYTHON_VER_FOLDER"
PYTHON_ALT_EXE="$PYTHON_ALT_FOLDER/bin/python$PYTHON_VER_FOLDER"

# Server
SERVER="python src/start-server"

#client upload
CLIENT_UPLOAD="python src/upload"

#client download
CLIENT_DOWNLOAD="python src/download"

testear(){
    TEST_NUMBER=$1
    TEST_FOLDER=$2
    SERVER_PARAMS=$3
    UPLOAD_PARAMS=$4
    DOWNLOAD_PARAMS=$5

    # comandos
    SERVER_EXE="$VALGRIND_FLAGS $SERVER $SERVER_PARAMS"
    CLIENT_UPLOAD_EXE="$VALGRIND_FLAGS $CLIENT_UPLOAD $UPLOAD_PARAMS"
    CLIENT_DOWNLOAD_EXE="$VALGRIND_FLAGS $CLIENT_DOWNLOAD $DOWNLOAD_PARAMS"

    # ejecuciones
    SERVER_OUT="${TEST_FOLDER}server_out_${TEST_NUMBER}.test"
    SERVER_OUT_CMP="${TEST_FOLDER}server_out_${TEST_NUMBER}.cmp"

    gnome-terminal -- sh -c "($SERVER_EXE > $SERVER_OUT) && exit;bash"

    UPLOAD_OUT_1="${TEST_FOLDER}upload_${TEST_NUMBER}.test"
    UPLOAD_OUT_1_CMP="${TEST_FOLDER}upload_${TEST_NUMBER}.cmp"

    gnome-terminal -- sh -c "($CLIENT_UPLOAD_EXE > ${UPLOAD_OUT_1}) && exit;bash"

    DOWNLOAD_OUT_1="${TEST_FOLDER}download_${TEST_NUMBER}.test"
    DOWNLOAD_OUT_1_CMP="${TEST_FOLDER}download_${TEST_NUMBER}.cmp"

    gnome-terminal -- sh -c "($CLIENT_DOWNLOAD_EXE > ${DOWNLOAD_OUT_1}) && exit;bash"

    sleep 15

    # comparaciones
    DIFF_FLAGS=" -u --no-dereference --new-file --ignore-trailing-space --strip-trailing-cr "

    SERVER_DIFF=$(diff ${DIFF_FLAGS} ${SERVER_OUT} $SERVER_OUT_CMP)
    UPLOAD_DIFF=$(diff ${DIFF_FLAGS} ${UPLOAD_OUT_1} $UPLOAD_OUT_1_CMP)
    DOWNLOAD_DIFF=$(diff ${DIFF_FLAGS} ${DOWNLOAD_OUT_1} $DOWNLOAD_OUT_1_CMP)

    echo -e "${AMARILLO}TEST [$TEST_NUMBER]: ${NC}"
    (test -z ${SERVER_DIFF} && echo -e "${GREEN} [$TEST_NUMBER] SERVER OK ${NC}" || echo -e "${RED} [$TEST_NUMBER] ERROR SERVER ${NC}") 2> /dev/null
    diff ${DIFF_FLAGS} ${SERVER_OUT} $SERVER_OUT_CMP

    (test -z ${UPLOAD_DIFF} && echo -e "${GREEN} [$TEST_NUMBER] UPLOAD OK ${NC}" || echo -e "${RED} [$TEST_NUMBER] ERROR UPLOAD${NC}") 2> /dev/null
    diff ${DIFF_FLAGS} ${UPLOAD_OUT_1} $UPLOAD_OUT_1_CMP

    (test -z ${DOWNLOAD_DIFF} && echo -e "${GREEN} [$TEST_NUMBER] DOWNLOAD OK ${NC}" || echo -e "${RED} [$TEST_NUMBER] ERROR DOWNLOAD${NC}") 2> /dev/null
    diff ${DIFF_FLAGS} ${DOWNLOAD_OUT_1} $DOWNLOAD_OUT_1_CMP

    rm ${TEST_FOLDER}*.test
}

# llamado de tests
TEST="1"
TEST_FOLDER_01="./tests/1/"
SERVER_PARAMS_1=" -h"
UPLOAD_PARAMS_1=" -h"
DOWNLOAD_PARAMS_1=" -h"
testear $TEST $TEST_FOLDER_01 $SERVER_PARAMS_1 $UPLOAD_PARAMS_1 $DOWNLOAD_PARAMS_1