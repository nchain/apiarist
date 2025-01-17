#!/bin/sh

# Create the root directory and geth / metrics directories
sudo mkdir -p {{ paths.root }}

{% if containers.geth_goerli %}
    sudo mkdir -p {{ paths.root }}/ethereum
{% endif %}

{% if containers.prometheus %}
    sudo mkdir -p {{ paths.root }}/prometheus
{% endif %}

# Create all the data directories for the bees to store their tasty honey
{% for i in range(bee_num) %}
sudo mkdir -p {{ paths.root }}/bee-{{ loop.index }}
sudo chown 65534:65534  {{ paths.root }}/bee-{{ loop.index }}
sudo chmod 777 {{ paths.root }}/bee-{{ loop.index }}
{% endfor %}

sudo cp ./password {{ paths.root }}/password
sudo chown 65534:65534 -R {{ paths.root }}/password
sudo chmod 775 {{ paths.root }}/password

# Let's setup clef to make sure it does its job of co-ordinating for our bees
{% if containers.clef %}
sudo mkdir -p {{ paths.root }}/clef/keystore
sudo cp -r {{ clef.keys_dir }}/UTC* {{ paths.root }}/clef/keystore/
sudo cp password {{ paths.root }}/clef/password
sudo chown 65534:0 -R {{ paths.root }}/clef
sudo chmod 750 {{ paths.root }}/clef
sudo sh -c "chmod -R 0600 {{ paths.root }}/clef/keystore/UTC*"
sudo sh clef.sh
{% endif %}

# Setup permissions for metrics gathering
[ -d "{{ paths.root }}/prometheus" ] && sudo chown 65534:65534 {{ paths.root }}/prometheus
[ -d "{{ paths.root }}/prometheus" ] && sudo chmod 755 {{ paths.root }}/prometheus

chmod +x monBee.sh

docker-compose up -d
docker container prune -f

{% if tearsheet %}
cat tearsheet.txt
{% endif %}