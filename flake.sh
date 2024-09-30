#!/bin/bash

YELLOW="\033[33m"
RESET="\033[0m"

function pause() {
 read -s -n 1 -p "Press any key to continue . . ."
 echo ""
}

echo -e "${YELLOW}upload${RESET}"
flake8 src/upload.py
echo
echo -e "${YELLOW}download${RESET}"
flake8 src/download.py
echo
echo -e "${YELLOW}start-server${RESET}"
flake8 src/start-server.py
echo
echo -e "${YELLOW}libs${RESET}"
flake8 src/lib/
echo

pause