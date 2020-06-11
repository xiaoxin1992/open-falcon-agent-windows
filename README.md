[![Python3](https://img.shields.io/badge/Python-3.8.3-blue.svg?style=popout&)](https://www.python.org/)
[![Open-Falcon](https://img.shields.io/badge/OpenFalcon-v0.3-orange.svg?style=popout)](http://www.open-falcon.com/)

# open-falcon-agent-windows
open-falcon indows Agent

### 使用方法
安装依赖
```
pip3 install -r requirements.txt
```
安装完Python以后需要执行build_exe.bat变成exe格式
W
````
c:\> .\build_exe.bat
57 INFO: PyInstaller: 3.6
57 INFO: Python: 3.8.3
60 INFO: Platform: Windows-10-10.0.18362-SP0
66 INFO: UPX is not available.
68 INFO: Extending PYTHONPATH with paths
71 INFO: checking Analysis
114 INFO: checking PYZ
127 INFO: checking PKG
176 INFO: Building PKG (CArchive) PKG-00.pkg
3131 INFO: Building PKG (CArchive) PKG-00.pkg completed successfully.
3144 INFO: Bootloader C:\Python38\lib\site-packages\PyInstaller\bootloader\Windows-64bit\run.exe
3144 INFO: checking EXE
3147 INFO: Rebuilding EXE-00.toc because agent.exe missing
3147 INFO: Building EXE from EXE-00.toc
3211 INFO: Copying icons from ['ico\\favicon.ico']
3212 INFO: Writing RT_GROUP_ICON 0 resource with 20 bytes
3214 INFO: Writing RT_ICON 1 resource with 4264 bytes
3219 INFO: Updating resource type 24 name 1 language 0
3234 INFO: Building EXE from EXE-00.toc completed successfully.
````
生成文件在dist目录中agent.exe, 请吧agent.exe和config.json放到一个目录中

### config.json 配置说明

````json
{
  "debug": true,
  "interval": 60,
  "heartbeat_addr": "127.0.0.1:6030",
  "transfer_addr": "127.0.0.1:8433",
  "version": "0.0.1",
  "plugins":[
    "CollectBasic"
  ]
}
````

参数 | 数值 |  说明  
-|-|-
debug | true/false | debug日志开关，否则只输出错误日志 |
interval | 60秒 | 数据采集提交 |
heartbeat_addr | 127.0.0.1:6030 | 心跳地址 |
transfer_addr | 127.0.0.1:8433 | 数据提交地址 |
plugins | ["CollectBasic"] | 插件配置 |

### 安装服务
```
agent.exe --startup auto install 并且设置服务自启动
agent.exe start  启动服务
```
### plugin 配置

```json
{
  "plugins":[
    "CollectBasic"
  ]
}
```

数组中的“CollectBasic”是插件类名称， 类名称配置在plugins包的__init__.py 中配置
```python
from .collect import CollectBasic
```

### 自定义采集类
自定义采集类需要继承 Metri 类, Metric定义如下

```python
class Metric:
    def make_data(self, metric, value, c_type="", tags="", timestamp=0):
        return {
            "endpoint": self.hostname,
            "metric": metric,
            "timestamp": timestamp,
            "step": self.push_interval,
            "value": value,
            "counterType": c_type,
            "tags": tags
        }
```
参数 |  示例 |  说明  
-|-|-
metric | agent.alive | Counters |
value | 10 | 采集的数值 |
c_type | GAUGE/COUNTER | 数据类型 |
tags | disk=c:\ | 标签 |
timestamp | 1591889163 | 采集时间戳 |

basic.py
```python
from datetime import datetime
from lib2.make_metric import Metric

class CollectBasicTest(Metric):
    def __init__(self, config):
        self.config = config
        self.zh_decode = "utf8"
        self.network_name = []
        self.timestamp = int(datetime.now().timestamp())

    def collect(self):
        """
          collect函数必须存在, 在执行plugin的时候调用获取数据 
        """
        logging.debug('enter basic collect')
        cpu_status = psutil.cpu_times_percent()
        metric = "cpu.user"
        value = cpu_status.user
        c_type = "GAUGE"
        result = self.make_data(metric, value, c_type=c_type, tags="", timestamp=self.timestamp)
        return result
```

文件放到plugins目录中， 并且在plugins 的__init__.py 文件增加
```python
from .basic import CollectBasicTest
```

重新执行build_exe.bat编译exe``c:\> .\build_exe.bat``，并重新安装服务，并且重启服务


使用Inno Setup Compiler 打包成安装包, 修改项目的pack目录中的build.iss
```#define ROOT "C:\github\open-falcon-agent-windows" 定义项目路径```
然后编译， 会在Output文件夹中生成agent-setup.exe， 双击即可安装