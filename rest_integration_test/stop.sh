#!/bin/bash

echo "Kill Process Start"
pgrep loop | xargs kill
iconservice stop -c ./conf/icon_conf1.json
rest stop -o ./conf/rest_config.json
echo "Kill Process Done"
