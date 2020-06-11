import socket
import itertools
import json
import logging
import encodings.idna


class Socket:
    def __init__(self, address, timeout=3):
        self.timeout = timeout
        self.address = address
        self.socket = None
        self.msg_id = itertools.count()

    def __enter__(self):
        self.socket = self.create_connection
        return self

    @property
    def create_connection(self):
        socket.setdefaulttimeout(int(self.timeout))
        try:
            return socket.create_connection(self.address.split(":"))
        except Exception as e:
            logging.error("{} create connect failure {}".format(self.address, str(e)))

    def send_recv(self, name, *params):
        data = {
            "id": next(self.msg_id),
            "params": params,
            "method": name
        }
        if self.socket is None:
            logging.error("connect create failure")
            return
        try:
            self.socket.sendall(json.dumps(data).encode())
            response = json.loads(self.socket.recv(4096))
            print(response, data)
            if response.get("id") != data["id"] or response["error"] is not None:
                logging.error("id={id} received id=[r_id], {error}".format(id=data["id"], r_id=response["id"],
                                                                           error=response["error"]))
            return response["result"]
        except Exception as e:
            logging.error("send data failure: {error}".format(error=e))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.socket is not None:
            self.socket.close()
