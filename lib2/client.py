import logging
from .sockets import Socket


class Sends:
    def send(self):
        for i in range(3):
            with Socket(self.addr) as socket:
                result = socket.send_recv(self.name, self.data)
                if result is not None:
                    logging.debug("send {}".format(result))
                    break
            logging.debug("send {} {} failure, times: {}".format(self.addr, self.name, i))
