import threading
import logging


class ThreadTask(threading.Thread):
    """
    搜集windows系统基础信息
    """

    def __init__(self, thread_id, name, obj, interval):
        super(ThreadTask, self).__init__()
        self.threadID = thread_id
        self.name = name
        self.daemon = True
        self.obj = obj
        self.interval = interval
        self._event = threading.Event()

    def terminate(self):
        self._event.set()

    def run(self):
        logging.debug("Starting " + self.name)
        while not self._event.isSet():
            if getattr(self.obj, "exec_plugin", None) is not None:
                self.obj.data = self.obj.exec_plugin()
            self.obj.send()
            self._event.wait(self.interval)
