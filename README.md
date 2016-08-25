# Ansible DNS dynamic inventory script
## Overview

This Python script, based upon [Remie Bolte's Node.js script to the same purpose](https://medium.com/@remie/using-dns-as-an-ansible-dynamic-inventory-e65a2ed6bc9#.wjoahpbd0), generates a dynamic inventory from specially formatted DNS TXT records. Output is in JSON.

It works by querying the specified domain for any TXT records matching two types of strings. The first specifies a hostname and any groups that host belongs to, using the following format:

     "hostname=tomcat01.example.com;groups=tomcat,webserver,texas"

Hosts without any specified groups will be added to the "ungrouped" group

The second string specifies any group_vars for a given group:

    "group=webserver;vars=foo_var:foo,bar_var:bar"

You can optionally specify host_vars on a hostname line, like so:

     "hostname=mysql.example.com;hostvars=foo_var:foo,bar_var:bar"
     "hostname=lab3.example.com;groups=lab;hostvars=foo_var:foo"

Output might look something like this:

```json
{
    "_meta": {
        "hostvars": {
            "mysql.example.com": {
                "foo_var": "foo",
                "bar_var": "bar"
            }
        }
    },
    "tomcat": {
        "hosts": [
            "tomcat01.example.com",
            "tomcat02.ptsteams.lab"
        ]
    },
    "lab": {
        "hosts": [
            "lab1.example.com"
            "lab2.example.com"
            "lab3.example.com"
        ],
        "vars": {
            "ansible_port": "22",
            "ansible_user": "matt"
        }
    },
    "ungrouped": {
        "hosts": [
            "mysql.example.com"
        ]
    },
    "webservers": {
        "hosts": [
            "webserver1.example.com"
            "webserver2.example.com"
        ]
    }
}
```


## Some things to keep in mind:
1. In an inventory, host_vars take precedence over group_vars.
2. Strings in TXT records are limited to 255 characters, but an individual
   record can be composed of multiple strings enclosed in double quotation 
   marks and separated by a space. Per [RFC 4408](https://www.ietf.org/rfc/rfc4408.txt)
   and [RFC 1035](https://www.ietf.org/rfc/rfc1035.txt), this script treats 
   multiple strings as if they are concatenated together. So a TXT record 
   like

   ```
     "group=db;vars=ansible_port:22" ",bar_var:bar"
   ```

   will be read as

   ```
   group=db;vars=ansible_port:22,bar_var:bar
   ```

3. DNS propagation can take time, as determined by a record's TTL value.
4. Do not to list sensitive information in TXT records.
5. You can get a listing of TXT records with: ```dig +short -t TXT example.com```
