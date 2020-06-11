from .client import Sends


class HBSClient(Sends):
    """
    open-falcon 心跳，在指定时间发送一次心跳
    """

    def __init__(self, config):
        self.addr = config.heartbeat_addr
        self.data = {
            "Hostname": config.hostname,
            "IP": config.address,
            "AgentVersion": "{version}".format(version=config.version),
            "PluginVersion": "plugins not enabled"
        }
        self.name = "Agent.ReportStatus"
