# rtsa-py-api

A Python wrapper module for the aaronia RTSA API

The module is based on the C++-Wrapper from the Aaronia-open-source library. It requires a Linux system and the Aaronia RTSA PRO Software.

## Getting started

### Basic Usage

The wrapper is designed to be used with context managers. Here is a basic example.
```
import rtsa-python-wrapper as rpw

with rpa.RTSAWrapper(rpa.AARTSAAPI_Wrapper_MemoryMode.MEDIUM) as api:
    devices = api.get_all_devices()
    with wrapper.instantiate_device(devices[0], rpw.AARTSAAPI_Wrapper_DeviceMode.RAW) as spectran:
        conf = spectran.get_config()
        root = {
            'main': {
                'centerfreq': { 'value': 2_440_000_000 },
                'decimation': { 'value': "Full" }
            }
        }
        conf.push_root_tree(root)
        root = conf.get_root_tree()
        conf.dump_config_tree(root, "conf.json")
        spectran.connect()
```
