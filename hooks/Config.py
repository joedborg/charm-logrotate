#!/usr/bin/python
#
# Copyright 2014 Canonical Ltd.  All rights reserved
# Author: Chris Stratford <chris.stratford@canonical.com>

import sys
import os
import json

sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))

from charmhelpers.core.hookenv import config, relation_get, in_relation_hook

class Config:
    compressExts = {"gzip": ".gz", "bzip2": ".bz2", "xz": ".xz"}

    def app_name(self):
        return str(config("application_name"))

    def compress(self, logname):
        return self.getConfig(logname, "compress")

    def compresscmd(self, logname):
        return self.getConfig(logname, "compresscmd")

    def compressext(self, logname):
        if self.compresscmd(logname) in self.compressExts:
            ext = self.compressExts[self.compresscmd(logname)]
        else:
            ext = ""
        return self.getConfig(logname, "compressext", ext)

    def dateext(self, logname):
        return self.getConfig(logname, "dateext")

    def path(self, logname):
        return str(self.logfile(logname)["path"])

    def getConfig(self, logname, what, default=""):
        if what in self.logfile(logname):
            return str(self.logfile(logname)[what])
        elif config(what):
            return config(what)
        else:
            return default

    def group(self, logname):
        return self.getConfig(logname, "group")

    def logfile(self, logname):
        l = self.logfiles()[logname]
        return l

    def logfiles(self):
        fromConfig = json.loads(str(config("logfiles")))
        if in_relation_hook():
            # Can't guarantee the data will be there
            try:
                fromRelation = json.loads(str(relation_get("logfiles")))
            except ValueError:
                fromRelation = {}
        else:
            fromRelation = {}
        # Local config overrides relation config
        return dict(fromRelation.items() + fromConfig.items())

    def owner(self, logname):
        return self.getConfig(logname, "owner")

    def period(self, logname):
        return self.getConfig(logname, "period")

    def perms(self, logname):
        return self.getConfig(logname, "perms")

    def postrotate(self, logname):
        return self.getConfig(logname, "postrotate")

    def prerotate(self, logname):
        return self.getConfig(logname, "prerotate")

    def when(self, logname):
        return self.getConfig(logname, "when")
