#!/usr/bin/python
#
# Copyright 2014 Canonical Ltd.  All rights reserved
# Author: Chris Stratford <chris.stratford@canonical.com>

import sys
import os
import os.path

sys.path.insert(0, os.path.join(os.environ['CHARM_DIR'], 'lib'))

from charmhelpers.core.hookenv import Hooks, log, charm_dir
from charmhelpers.fetch import apt_install, apt_update
from Cheetah.Template import Template
from Config import Config

hooks = Hooks()
conf = Config()

required_pkgs = [
    "logrotate",
    "gzip",
    "bzip2",
    "xz-utils",
]

def juju_header():
    header = ("#-------------------------------------------------#\n"
              "# This file is Juju managed - do not edit by hand #\n"
              "#-------------------------------------------------#\n")
    return header

def file_from_template(tmpl, dest, searchList):
    template_file = os.path.join(charm_dir(), "templates", tmpl)
    t = Template(file=template_file, searchList=searchList)
    with open(dest, "w") as f:
        f.write(juju_header())
        f.write(str(t))
    os.chmod(dest, 0444)


def install_packages():
    apt_update()
    apt_install(required_pkgs, options=['--force-yes'])


def configure_logrotate():
    for logname in conf.logfiles():
        log("CHARM: Adding logrotate entry for {}".format(logname))
        tmpl_data = {}
        tmpl_data["path"] = conf.path(logname)
        tmpl_data["when"] = conf.when(logname)
        tmpl_data["compress"] = conf.compress(logname)
        tmpl_data["compresscmd"] = conf.compresscmd(logname)
        tmpl_data["compressext"] = conf.compressext(logname)
        tmpl_data["dateext"] = conf.dateext(logname)
        tmpl_data["period"] = conf.period(logname)
        tmpl_data["perms"] = conf.perms(logname)
        tmpl_data["owner"] = conf.owner(logname)
        tmpl_data["group"] = conf.group(logname)
        tmpl_data["prerotate"] = conf.prerotate(logname)
        tmpl_data["postrotate"] = conf.postrotate(logname)
        logrotate_path = "/etc/logrotate.d/{}".format(logname)
        file_from_template("logrotate.tmpl", logrotate_path, tmpl_data)
        os.chmod(logrotate_path, 0444)


@hooks.hook("install")
def install():
    log("CHARM: Installing {}".format(conf.app_name()))
    install_packages()


@hooks.hook("upgrade-charm")
def upgrade_charm():
    log("CHARM: Upgrading {}".format(conf.app_name()))


@hooks.hook("config-changed")
def config_changed():
    log("CHARM: Configuring {}".format(conf.app_name()))
    configure_logrotate()


@hooks.hook("logrotate-relation-changed")
def logrotate_relation_changed():
    log("CHARM: Logrotate relation changed {}".format(conf.app_name()))
    configure_logrotate()


@hooks.hook("start")
def start():
    # Nothing to start - just here to keep charm proof happy
    log("CHARM: Starting {}".format(conf.app_name()))


@hooks.hook("stop")
def stop():
    # Nothing to stop - just here to keep charm proof happy
    log("CHARM: Stopping {}".format(conf.app_name()))


if __name__ == "__main__":
    hooks.execute(sys.argv)
