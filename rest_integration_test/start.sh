#!/bin/bash

# source ../venv/bin/activate

loop rs -d -o ./conf/loop_rs_conf.json &
sleep 3

iconservice start -c ./conf/icon_conf1.json
sleep 3

loop peer -d -r 127.0.0.1:7102 -o ./conf/loop_peer_conf1.json &
sleep 3

rest start -o ./conf/rest_config.json
