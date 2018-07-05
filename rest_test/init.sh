#!/bin/bash

# sudo apt install rabbitmq-server

#virtualenv -p python3 venv

deactivate
source ./venv/bin/activate

echo "uninstall package start!"
pip uninstall -y tbears
pip uninstall -y iconservice
pip uninstall -y earlgrey
pip uninstall -y loopchain
pip uninstall -y rest

echo "install package start"
pip install ./lib/earlgrey-0.0.0-py3-none-any.whl
pip install ./lib/iconservice-0.9.2-py3-none-any.whl
pip install ./lib/tbears-0.9.2-py3-none-any.whl
pip install ./lib/loopchain-1.21.0-py3-none-any.whl
pip install ./lib/rest-0.9.2-py3-none-any.whl