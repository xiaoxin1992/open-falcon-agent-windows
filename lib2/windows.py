import wmi


class System:
    def __init__(self):
        wmi_obj = wmi.WMI()
        self.system = wmi_obj.Win32_OperatingSystem()[0]
        self.ips = wmi_obj.Win32_NetworkAdapterConfiguration()

    @property
    def hostname(self):
        return self.system.CSName

    @property
    def address(self):
        return [ip.IPAddress[0].strip() for ip in self.ips if
                ip.IPAddress is not None and ip.IPAddress[0].strip() != "127.0.0.1"]
