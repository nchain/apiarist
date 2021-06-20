#!/usr/bin/bash

sudo apt-get install -y npm
sudo apt-get install -y python3-pip
sudo pip3 install -y virtualenv 

pip install PyYAML

# install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

docker network create bee_hive

mv ./bin/docker-compose-Linux-x86_64 /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose