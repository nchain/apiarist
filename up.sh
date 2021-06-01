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
HIVE_YAML=/data/hive/hive.yml
[ ! -f "$HIVE_YAML" ] && echo "no hive.yml found in /data/hive" && exit 1

python build.py $HIVE_YAML

# Deploy to docker-compose
sh deploy.sh

# Install monBee dependencies
cd monBee
npm i