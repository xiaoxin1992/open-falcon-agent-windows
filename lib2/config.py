# -*- coding:utf8 -*-
import os

import json
from collections import namedtuple
from lib2.windows import System


def config(root):
    config_path = os.path.join(root, "config.json")
    if not os.path.exists(config_path) or not os.path.isfile(config_path):
        return None
    system = System()
    with open(config_path, encoding="utf8") as f:
        config_data = json.load(f)
    data = namedtuple("data", "debug interval heartbeat_addr transfer_addr version plugins hostname address")
    data.interval = config_data["interval"]
    data.heartbeat_addr = config_data["heartbeat_addr"]
    data.transfer_addr = config_data["transfer_addr"]
    data.debug = config_data["debug"]
    data.version = config_data["version"]
    data.plugins = config_data["plugins"]
    data.hostname = system.hostname
    data.address = "127.0.0.1" if len(system.address) else system.address[0]
    return data
