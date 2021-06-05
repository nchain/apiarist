#!/bin/sh

# Make sure submodules etc are updated.
git submodule update --init --recursive

VENV=$(which virtualenv)
# First make sure a python virtual environment is installed
$VENV .virtualenv
source ./.virtualenv/bin/activate

# Install the requirements
pip3 install -r requirements.txt

# Now, generate all the files, including deploy.sh
HIVE_YAML=$1
[ -z "$HIVE_YAML" ] && HIVE_YAML="$HOME/.hive.yml"
[ ! -f "$HIVE_YAML" ] && echo "$HOME/.hive.yml not found" && exit 1

sudo python build.py $HIVE_YAML

# Deploy to docker-compose
sh deploy.sh

# Install monBee dependencies
cd monBee
npm i