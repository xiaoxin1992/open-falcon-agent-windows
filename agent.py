# -*- coding:utf8 -*-
import inspect

import win32serviceutil
import win32service
import win32event
import win32timezone
import os
import sys
import logging
from lib2.config import config
import pythoncom
import servicemanager
from lib2.hbs import HBSClient
from lib2.transfer import TransferClient
from lib2.tasks import ThreadTask
import plugins


class Transfer(TransferClient):
    def __init__(self, config):
        self.config = config
        super(Transfer, self).__init__(self.config)

    def exec_plugin(self):
        result = []
        for plugin in self.config.plugins:
            plugin_obj = getattr(plugins, plugin, None)
            if plugin_obj is None:
                logging.error("Unable to get plugins {plugin}".format(plugin=plugin))
                continue
            plugin_obj = plugin_obj(self.config)
            if getattr(plugin_obj, "collect", None) is None:
                logging.error("Unable to get function collect".format(plugin=plugin))
                continue
            result = plugin_obj.collect()
            if isinstance(result, list):
                result.extend(result)
            elif isinstance(result, dict):
                result.append(result)
            else:
                logging.error("{plugin} Incorrect format of collected data {data}".format(plugin=plugin, data=result))
                continue
        return result


class AgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'Agent'
    _svc_display_name_ = 'Agent'
    _svc_description_ = 'cmdb & Open Falcon Windows Agent'

    def __init__(self, args):
        pythoncom.CoInitialize()
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.task_id = []
        self.root = os.path.dirname(sys.executable)
        self.config = config(self.root)
        if self.config.debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(filename=os.path.join(self.root, 'service.log'), level=level,
                            format='%(asctime)s %(filename)-12s %(levelname)-8s %(message)s')
        self.run = True

    def SvcDoRun(self):
        logging.debug('service is run...')
        self.task_id = [ThreadTask(1, "transfer", Transfer(self.config), self.config.interval),
                        ThreadTask(2, "hbs", HBSClient(self.config), self.config.interval)]
        for i in self.task_id:
            i.start()
        for j in self.task_id:
            j.join()

    def SvcStop(self):
        logging.debug('service is stop.')
        for s_stop in self.task_id:
            s_stop.terminate()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


if __name__ == '__main__':

    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(AgentService)
            servicemanager.Initialize('AgentService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            import winerror

            if details == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(AgentService)
