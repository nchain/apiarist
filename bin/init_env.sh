#!/usr/bin/bash

sudo apt-get install -y jq
sudo apt-get install -y npm
sudo apt-get install -y python3-pip
sudo pip3 install virtualenv 

pip install PyYAML

docker network ls |grep bee_hive || docker network create bee_hive