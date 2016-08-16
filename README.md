# Ansible DNS dynamic inventory script

This Python script generates a dynamic inventory from specially formatted DNS TXT records. Output is in JSON.

It works by querying the specified domain for any TXT records matching two types of strings. The first specifies a hostname and any groups that host belongs to, using the following format:

     "hostname=tomcat.example.com;groups=tomcat,webserver,texas"

The second specifies any group_vars for a given group:

     "group=webserver;vars=foo_var:foo,bar_var:bar"

You can optionally specify host_vars on a hostname line:

    "hostname=mysql.example.com;hostvars=foo_var:foo,bar_var:bar"
     "hostname=lab7.example.com;groups=lab;hostvars=foo_var:foo"

Some things to keep in mind:
- In an inventory, host_vars take precedence over group_vars.
- Strings in TXT records are limited to 255 characters, but an individual
  record can be composed of multiple strings separated by double quotation
  marks. Multiple strings are treated as if they are concatenated together.
  (See [RFC 4408](https://www.ietf.org/rfc/rfc4408.txt) and [RFC 1035](https://www.ietf.org/rfc/rfc1035.txt) for technical details.) So a TXT record like

   ```bash
     "group=db;vars=ansible_port:22" ",bar_var:bar"
   ```     

   will be read as

   ```bash  
   group=db;vars=ansible_port:22,bar_var:bar
   ```

- DNS propagation can take time, as determined by a record's TTL value.
- Do not to list sensitive information in TXT records.
- You can get a listing of TXT records with: 'dig +short -t TXT example.com'
