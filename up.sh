#!/bin/sh

# Make sure submodules etc are updated.
# git submodule update --init --recursive

VENV=$(which virtualenv)
# First make sure a python virtual environment is installed
mkdir -p .virtualenv
$VENV .virtualenv
. ./.virtualenv/bin/activate

# Install the requirements
pip3 install -r requirements.txt

# Now, generate all the files, including deploy.sh
HIVE_YAML=$1
[ -z "$HIVE_YAML" ] && HIVE_YAML="$HOME/.config/swarm/hive.yml"
[ ! -f "$HIVE_YAML" ] && echo "$HIVE_YAML not found" && exit 1
clef_keys_dir="$HOME/.config/swarm/clef_keys"
mkdir -p $clef_keys_dir

python3 build.py $HIVE_YAML

# Deploy to docker-compose
sh deploy.sh

# Install monBee dependencies
cd monBee
npm i