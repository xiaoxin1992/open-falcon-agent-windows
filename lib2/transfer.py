from .client import Sends


class TransferClient(Sends):
    def __init__(self, config):
        self.addr = config.transfer_addr
        self.name = "Transfer.Update"
        self.data = {}
