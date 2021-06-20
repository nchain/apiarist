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
HIVE_CONFIG_DIR = os.path.dirname(os.path.abspath(HIVE_YAML))
HIVE_KEYS_DIR = HIVE_CONFIG_DIR + "/clef_keys"
HIVE_ACCOUNTS = HIVE_CONFIG_DIR + "/accounts"

with open(HIVE_YAML, 'r') as f:
    hiveYaml = yaml.load(f, Loader=yaml.FullLoader)

# Number of bees at the queen's service should she choose.
bee_num =                 hiveYaml['bee_num']

# Every bee has it's day
versions = {
    'clef':                 hiveYaml['versions']['clef'],
    'bee':                  hiveYaml['versions']['bee'],
    'geth':                 hiveYaml['versions']['geth']
}

# whether to show the result or not
tearsheet =                 hiveYaml['tearsheet']

# Where do we keep the sweet honey
paths = {
    'root':                 hiveYaml['root_path'],
}

# The clef password - used to encrypt new ethereum accounts.
# WARNING: THIS MUST BE AT LEAST 10 CHARACTERS LONG.
#          REFER TO https://geth.ethereum.org/docs/getting-started
clef = {
    'password':             hiveYaml['clef']['password'],
    'location':             hiveYaml['clef']['location']
}

goerli = {
    'location' :            hiveYaml['goerli']['location']
}

# Network port settings - let's make it easier to share pollen!
network = {
    'base_host_port':       hiveYaml['base_host_port'],
    'base_external_port':   hiveYaml['base_external_port'],
    'host_ip_addr':         hiveYaml['host_ip_addr'],
    'external_ip_addr':     hiveYaml['external_ip_addr'],
    'grafana_port':         hiveYaml['grafana_port'],
    'geth_http_port':       hiveYaml['geth_http_port'],
    'geth_ws_port':         hiveYaml['geth_ws_port'],
}

containers = {
    'prometheus':           hiveYaml['containers']['prometheus'],
    'cadvisor':             hiveYaml['containers']['cadvisor'],
    'node_exporter':        hiveYaml['containers']['node-exporter'],
    'alertmanager':         hiveYaml['containers']['alertmanager'],
    'grafana':              hiveYaml['containers']['grafana'],
    'geth_goerli':          hiveYaml['containers']['geth-goerli'],
    'geth_goerli_exporter': hiveYaml['containers']['geth-goerli-exporter'],
    'clef':                 hiveYaml['containers']['clef'],
    'bees':                 hiveYaml['containers']['bees'],
}

bee_host_ips =              hiveYaml['bee_host_ips']

if containers['clef']:
    # First let's go through existing Ethereum accounts for the
    # nodes.
    accounts = []
    clef_key_p =  HIVE_KEYS_DIR + "/UTC*"

    step = 0
    for keyfile in glob.glob( clef_key_p ):
        step += 1
        encrypted = open(keyfile).read()
        decrypted = Account.decrypt(encrypted, clef["password"])
        acct = Account.from_key( decrypted )
        pretty_address = acct.address[2:].lower()
        print( '%d : loaded acct: [%s]' %(step, pretty_address) )
        accounts.append(acct)

    curr_size = len(accounts)
    print ('loaded %d existing accounts' % (curr_size))

    accounts_f = open(HIVE_ACCOUNTS, 'w')

    # Second let's create new Ethereum accounts for the
    # nodes.
    if (curr_size < bee_num):
        extra_len = bee_num - curr_size
        Account.enable_unaudited_hdwallet_features()
        extra_accounts = [ Account.create() for x in range(extra_len) ]
        steps = 0
        for account in extra_accounts:
            # Encrypt all the node's private keys and store them into clef.
            # This is why clef's password is required.
            steps += 1
            encrypted = account.encrypt(clef['password'])
            now = datetime.utcnow()
            pretty_address = account.address[2:].lower()
            accounts_f.writelines(pretty_address + "\n")

            file_name = "UTC--{}--{}".format(
                now.strftime("%Y-%m-%dT%H-%M-%S.%f"),
                pretty_address
            )
            accounts.append(account)

            # Let's save it in a file format hopefully usable by clef
            with open(HIVE_KEYS_DIR + '/' + file_name, 'w') as f:
                f.write(json.dumps(encrypted))
            
            print('[%d] created new acct: [%s]' % (steps, pretty_address))
    
    accounts_f.close()

if containers['bees']:
    accounts = []
    with open(HIVE_ACCOUNTS, 'r') as f:
        lines = f.readlines()
        for line in lines:
            accounts.append(line)

print('Total accounts loaded: %d ' % (len(accounts)) )

file_loader = FileSystemLoader('templates')
env = Environment(
    loader=file_loader, trim_blocks=True, lstrip_blocks=True
)

# Process a template file
def process(input, output):
    # Process the docker-compose.yaml
    template = env.get_template(input)

    rendered = template.render(
        bee_num=bee_num, paths=paths, clef=clef, goerli=goerli, network=network,
        versions=versions, accounts=accounts, containers=containers,
        bee_host_ips=bee_host_ips
    )

    with open(output, 'w') as f:
        f.write(rendered)

templates = [
    ('docker.txt', 'docker-compose.yaml'),
    ('env.ini', '.env'),
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
