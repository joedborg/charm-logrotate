# Overview
This charm provides a simple way for charms to add log rotation or
for an admin to rotate files not otherwise managed.

# Configuration

There are several settings that configure defaults:

* **when** When the logs should be rotated (daily, weekly, etc.)
* **period** How many logs we should keep before they get deleted
* **perms** Logfile permissions (as chmod)
* **owner** Logfile owner
* **group** Logfile group
* **dateext** Use dateext? (true or false)
* **compress** Compress the logs or not (compress or nocompress)
* **compresscmd** What command to compress with (gzip, bzip2 or xz)
* **compressext** What file extension to use for compressed files (determined
automatically if not set)

## Admin-Controlled Usage
If you want to rotate un-managed files, this is what you want.
You will still need to add a relation to one of your existing services
(it will use the juju-info interface), as this is a subordinate charm,
but logrotate will not interact with that service (just files that happen
to share the same unit).

There is a per-logfile config setting:

**logfiles** Provides local logfile settings or overrides package or
charmed log rotation.

As there could be many variations, the logfiles setting is a JSON-format
string, set out as follows:

`{"first_logfile_name":{"path":"/path/to/logs/*.log", "option":"value", ...}}`

Where *option* can be any of the above settings plus two additional
ones: *prerotate* and *postrotate* which supply pre- and post-rotation commands.

Per-logfile options will override the default settings.

To manage more than one file, just extend the logfiles string:

`{"logfile1": {<local settings>}, "logfile2", {<local settings>}}`


## Charm-Controlled Usage
It is also possible for a charm to manage its own log rotation using
the logrotate subordinate charm.  A "logrotate" interface is provided
for this.

Used like this, you can still have manually-managed log rotation - these
will be added to whatever the related charm configures.

Passing the above "logfiles" JSON string in the charm's relation
data from a logrotate-relation-changed hook should be all that's needed.

For example:

```
from charmhelpers.core.hookenv import relation_set, relation_id, relation_ids

def update_logrotate():
    relation_data = {}
    relation_data["logfiles"] = '{"apache2":{"path":"/var/log/apache2/*.log","when":"daily","period":"7"}}'
    if relation_id():
        relation_set(None, relation_data)
    else:
        for r in relation_ids("logrotate"):
            relation_set(r, relation_data)
```

## Notes
Charm-controlled log-rotation through the logrotate interface can be
overridden by a matching entry in the *logfiles* config option.  For
example, if a charm sets weekly rotation on "mylogfiles" using the
logrotate relation interface:

`relation_data["logfiles"] = '{"mylogfiles":{"path":"/var/log/mycharm/*.log","when":"weekly"}}'`

But the admin wants them rotated daily, they just need to:

`juju set logrotate logfiles='{"mylogfiles":{"path":"/var/log/mycharm/*.log","when":"daily"}}'`

# Example
```
juju add-unit apache2
juju add-unit logrotate
juju set logrotate logfiles='{"apache2":{"path":"/var/log/apache2/*.log","when":"daily","period":"28"}}'
juju add-relation apache2 logrotate
```

