import psutil
from datetime import datetime
import logging
from lib2.make_metric import Metric


class CollectBasic(Metric):

    def __init__(self, config):
        self.old_network = {
            "recv": {},
            "sent": {}
        }
        self.push_interval = config.interval
        self.zh_decode = "utf8"
        self.network_name = []
        self.timestamp = int(datetime.now().timestamp())

    @staticmethod
    def make_disk_status(payload, disk_status):
        for disk in disk_status:
            if 'cdrom' in disk.opts or disk.fstype == '':
                continue
            tag = "disk=" + disk.device.split(":")[0]
            disk_info = psutil.disk_usage(disk.mountpoint)
            payload.append(("df.used.percent", disk_info.percent, "GAUGE", tag))
            payload.append(("df.byte.total", disk_info.total, "GAUGE", tag))
            payload.append(("df.byte.used", disk_info.used, "GAUGE", tag))
            payload.append(("df.byte.free", disk_info.free, "GAUGE", tag))

    @staticmethod
    def make_disk_io_status(payload, disk_io_status):
        for key in disk_io_status:
            tag = "device=" + key
            payload.append(("disk.io.read_count", disk_io_status[key].read_count, "COUNTER", tag))
            payload.append(("disk.io.write_count", disk_io_status[key].write_count, "COUNTER", tag))
            payload.append(("disk.io.read_bytes", disk_io_status[key].read_bytes, "COUNTER", tag))
            payload.append(("disk.io.write_bytes", disk_io_status[key].write_bytes, "COUNTER", tag))
            payload.append(("disk.io.read_time", disk_io_status[key].read_time, "COUNTER", tag))
            payload.append(("disk.io.write_time", disk_io_status[key].write_time, "COUNTER", tag))

    def network_io_status(self, payload, net_io_status):
        for key in net_io_status:
            if self.is_lookup(key):
                continue
            tag = "interface=" + key.encode("utf8").decode(self.zh_decode)
            payload.append(("net.if.in.mbits", net_io_status[key].bytes_recv * 8 / 100000, "COUNTER", tag))
            payload.append(("net.if.out.mbits", net_io_status[key].bytes_sent * 8 / 100000, "COUNTER", tag))
            payload.append(("net.if.in.packets", net_io_status[key].packets_recv, "COUNTER", tag))
            payload.append(("net.if.out.packets", net_io_status[key].packets_sent, "COUNTER", tag))
            payload.append(("net.if.in.error", net_io_status[key].errin, "COUNTER", tag))
            payload.append(("net.if.out.error", net_io_status[key].errout, "COUNTER", tag))
            payload.append(("net.if.in.drop", net_io_status[key].dropin, "COUNTER", tag))
            payload.append(("net.if.out.drop", net_io_status[key].dropout, "COUNTER", tag))
            logging.debug(payload)

    @staticmethod
    def is_lookup(network_name):
        if network_name == "Loopback Pseudo-Interface 1":
            return True
        else:
            return False

    def network_flow_handle(self, item, data):
        tmp_data = []
        network_flow = self.old_network.get(item, None)
        for key, value in data.items():
            if item == "recv":
                bytes_data = value.bytes_recv
            else:
                bytes_data = value.bytes_sent
            if self.is_lookup(key):
                continue
            if network_flow is None or network_flow.get(key, None) is None:
                tmp_data.append((key, 0))
            else:
                # Kbps
                bps = (bytes_data - network_flow[key][0]) / (self.timestamp - network_flow[key][1]) / 1000.0 * 8
                tmp_data.append((key, bps))
            self.old_network[item][key] = (bytes_data, self.timestamp)
        return tmp_data

    def network_flow(self, payload, net_flow_status):
        recv = []
        sent = []
        for key, value in net_flow_status.items():
            if key == "recv":
                recv = self.network_flow_handle("recv", value)
            else:
                sent = self.network_flow_handle("sent", value)
        for rec in recv:
            sent_data = list(filter(lambda x: x[0] == rec[0], sent))[0][1]
            tag = "network_flow=" + rec[0]
            payload.append(("flow.in.kbps", rec[1], "GAUGE", tag))
            payload.append(("flow.out.kbps", sent_data, "GAUGE", tag))

    def collect(self):
        logging.debug('enter basic collect')
        cpu_status = psutil.cpu_times_percent()
        mem_status = psutil.virtual_memory()
        swap_status = psutil.swap_memory()
        disk_io_status = psutil.disk_io_counters(perdisk=True)
        disk_status = psutil.disk_partitions()
        net_io_status = psutil.net_io_counters(pernic=True)
        self.network_name = net_io_status.keys()
        net_flow_status = {
            "recv": psutil.net_io_counters(pernic=True),
            "sent": psutil.net_io_counters(pernic=True)
        }
        payload = [
            ("agent.alive", 1, "GAUGE"),
            ("cpu.user", cpu_status.user, "GAUGE"),
            ("cpu.system", cpu_status.system, "GAUGE"),
            ("cpu.idle", cpu_status.idle, "GAUGE"),
            ("mem.memused.percent", mem_status.percent, "GAUGE"),
            ("mem.swapused.percent", swap_status.percent, "GAUGE"),
        ]
        self.make_disk_status(payload, disk_status)
        self.make_disk_io_status(payload, disk_io_status)
        self.network_io_status(payload, net_io_status)
        self.network_flow(payload, net_flow_status)
        return self.make(payload)

    def make(self, payload):
        data = []
        for i in payload:
            data.append(self.make_data(*i, timestamp=self.timestamp))
        return data
