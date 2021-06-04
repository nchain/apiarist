#
# Author mfw78@chasingseed.com
#

import os
from jinja2 import Environment, FileSystemLoader
from eth_account import Account
from datetime import datetime
import time
import json
import sys
import yaml
import glob

HIVE_YAML = sys.argv[1]
with open(HIVE_YAML, 'r') as f:
    hiveYaml = yaml.load(f, Loader=yaml.FullLoader)

# Number of bees at the queen's service should she choose.
num_nodes = hiveYaml['num_nodes']

# Every bee has it's day
versions = {
    'clef': hiveYaml['versions']['clef'],
    'bee': hiveYaml['versions']['bee'],
    'geth': hiveYaml['versions']['geth']
}

# Where do we keep the sweet honey
paths = {
    'root': hiveYaml['root_path'],
}

# The clef password - used to encrypt new ethereum accounts.
# WARNING: THIS MUST BE AT LEAST 10 CHARACTERS LONG.
#          REFER TO https://geth.ethereum.org/docs/getting-started
clef = {
    'password': hiveYaml['clef_password']
}

# Network port settings - let's make it easier to share pollen!
network = {
    'base_host_port': hiveYaml['base_host_port'],
    'base_external_port': hiveYaml['base_external_port'],
    'host_ip_addr': hiveYaml['host_ip_addr'],
    'external_ip_addr': hiveYaml['external_ip_addr'],
    'grafana_port': hiveYaml['grafana_port'],
    'geth_http_port': hiveYaml['geth_http_port'],
    'geth_ws_port': hiveYaml['geth_ws_port'],
}

containers = {
    'prometheus': hiveYaml['containers']['prometheus'],
    'cadvisor': hiveYaml['containers']['cadvisor'],
    'node_exporter': hiveYaml['containers']['node-exporter'],
    'alertmanager': hiveYaml['containers']['alertmanager'],
    'grafana': hiveYaml['containers']['grafana'],
    'geth_goerli': hiveYaml['containers']['geth-goerli'],
    'geth_goerli_exporter': hiveYaml['containers']['geth-goerli-exporter'],
    'clef': hiveYaml['containers']['clef'],
    'bees': hiveYaml['containers']['bees'],
}

host_pub_ips = hiveYaml['host_pub_ips']

# First let's go through existing Ethereum accounts for the
# nodes.
accounts = []
keys = glob.glob( paths["root"] + "/clef/keystore/UTC*" )
for key in keys:
    encrypted = open(key).read()
    decrypted = Account.decrypt(encrypted, clef["password"])
    acct = Account.from_key( decrypted )
    accounts.append(acct)

# Second let's create new Ethereum accounts for the
# nodes.
curr_size = len(keys)
if (curr_size < num_nodes):
    extra_len = num_nodes - curr_size
    Account.enable_unaudited_hdwallet_features()
    extra_accounts = [ Account.create() for x in range(extra_len) ]
    for account in extra_accounts:
        # Encrypt all the node's private keys and store them into clef.
        # This is why clef's password is required.
        encrypted = account.encrypt(clef['password'])
        now = datetime.utcnow()
        pretty_address = account.address[2:].lower()

        file_name = "UTC--{}--{}".format(
            now.strftime("%Y-%m-%dT%H-%M-%S.%f"),
            pretty_address
        )
        accounts.append(account)

        # Let's save it in a file format hopefully usable by clef
        with open(file_name, 'w') as f:
            f.write(json.dumps(encrypted))
  

file_loader = FileSystemLoader('templates')
env = Environment(
    loader=file_loader, trim_blocks=True, lstrip_blocks=True
)

# Process a template file
def process(input, output):
    # Process the docker-compose.yaml
    template = env.get_template(input)

    rendered = template.render(
        num_nodes=num_nodes, paths=paths, clef=clef, network=network,
        versions=versions, accounts=accounts, containers=containers, 
        host_pub_ips=host_pub_ips
    )

    with open(output, 'w') as f:
        f.write(rendered)

templates = [
    ('docker.txt', 'docker-compose.yaml'),
    ('env.txt', '.env'),
    ('password.txt', 'password'),
    ('clef.txt', 'clef.sh'),
    ('deploy.txt', 'deploy.sh'),
    ('prometheus.txt', 'prometheus/prometheus.yml'),
    ('tearsheet.txt', 'tearsheet.txt'),
    ('monBee.txt', 'monBee.sh')
]

# Process the templates
for t in templates:
    process(*t)

os.chmod("deploy.sh", 0o755)
