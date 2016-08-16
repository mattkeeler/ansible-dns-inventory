#!/usr/bin/env python

###############################################################################
# Dynamic DNS inventory script for Ansible
#
# Based upon Remie Bolte's Node.js script to the same purpose
# (https://medium.com/@remie/using-dns-as-an-ansible-dynamic-inventory-e65a2ed6bc9#.wjoahpbd0)
#
# This Python script generates a dynamic inventory from specially formatted
# DNS TXT records. Output is in JSON.
#
# It works by querying the specified domain for any TXT records matching two
# types of strings. The first specifies a hostname and any groups that host
# belongs to, using the following format:
#
#     "hostname=tomcat.example.com;groups=tomcat,webserver,texas"
#
# The second specifies any group_vars for a given group:
#
#     "group=webserver;vars=foo_var:foo,bar_var:bar"
#
# You can optionally specify host_vars on a hostname line:
#
#     "hostname=mysql.example.com;hostvars=foo_var:foo,bar_var:bar"
#     "hostname=lab7.example.com;groups=lab;hostvars=foo_var:foo"
#
# Some things to keep in mind:
# - In an inventory, host_vars take precedence over group_vars.
# - Strings in TXT records are limited to 255 characters, but an individual
#   record can be composed of multiple strings separated by double quotation
#   marks. Multiple strings are treated as if they are concatenated together.
#   (See RFC 4408 and RFC 1035 for technical details.) So a TXT record like
#       "group=db;vars=ansible_port:22" ",bar_var:bar"
#   will be read as
#       group=db;vars=ansible_port:22,bar_var:bar
# - DNS propagation can take time, as determined by a record's TTL value.
# - Do not to list sensitive information in TXT records.
# - You can get a listing of TXT records with: 'dig +short -t TXT example.com'
###############################################################################

import dns.resolver
import argparse
import sys
from collections import defaultdict
import json

# The domain we are querying.
domain = 'ptsteams.lab'
# We sort results in reverse alphabetical order to make parsing easier.
records = sorted(dns.resolver.query(domain, 'TXT'), reverse=True)

class DNSInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.dns_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print json.dumps(self.inventory, indent=4);

    # Generate our DNS inventory
    def dns_inventory(self):
        inventory = defaultdict(list)
        for record in records:
            store = {}
            stripquotes = str(record).replace('"', '')
            data = str(stripquotes).replace(' ', '').split(';')
            for item in data:
                key, value = str(item).split('=')
                store[key] = value
            if 'hostname' in store:
                if 'groups' in store:
                    for group in store['groups'].split(','):
                        if group not in inventory:
                            inventory[group] = {'hosts': []}
                        inventory[group]['hosts'].append(store['hostname'])
                elif 'groups' not in store:
                    if 'ungrouped' not in inventory:
                        inventory['ungrouped'] = {'hosts': []}
                    inventory['ungrouped']['hosts'].append(store['hostname'])
                if 'hostvars' in store:
                    for hostvar in store['hostvars'].split(','):
                        if '_meta' not in inventory:
                            inventory['_meta'] = {'hostvars': {}}
                        if store['hostname'] not in inventory['_meta']['hostvars']:
                            inventory['_meta']['hostvars'][store['hostname']] = {}
                        var, val = hostvar.split(':')
                        inventory['_meta']['hostvars'][store['hostname']].update({var: val})
            elif ('group' in store) and ('vars' in store):
                for group in inventory:
                    if store['group'] == group:
                        if 'vars' not in group:
                            inventory[group].update({'vars': {}})
                        for groupvar in store['vars'].split(','):
                            var, val = groupvar.split(':')
                            inventory[group]['vars'].update({var: val})
        return(inventory)


    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}


    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

# Get the inventory
DNSInventory()
