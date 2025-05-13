# rtsa-py-api

A Python wrapper module for the aaronia RTSA API

The module is based on the C++-Wrapper from the Aaronia-open-source library. It requires a Linux system and the Aaronia RTSA PRO Software.

## Getting started

### Basic Usage

The wrapper is designed to be used with context managers. Here is a basic example.
```python=
import rtsa-python-wrapper as rpw

with rpa.RTSAWrapper(rpa.AARTSAAPI_Wrapper_MemoryMode.MEDIUM) as wrapper:
    devices = wrapper.get_all_devices()
    with wrapper.instantiate_device(devices[0], rpw.AARTSAAPI_Wrapper_DeviceMode.RAW) as device:
        device_config = {
            'calibration': {
                'rffilter': { 'value': 'Bypass'},
                'preamp': { 'value': 'Preamp' },
                # 'calibrationmode': {'value': 'RX Attenuator'}
            },
            'device': {
                'outputformat': { 'value': "iq" },
                'triggeredge': { 'value': "High" },
                'triggerflag': { 'value': "C0" },
                # 'gaincontrol': { 'value': "power" }
            },
            'main': {
                'centerfreq': { 'value': 125_000_000 },
                'decimation': { 'value': "Full" },
                'reflevel': { 'value': -20.0 },
            }
        }
        device.push_config(device_config)
        device.start()
        packet = device.get_packet()
```
The first contextmanager starts the rtsa api to get a list of devices. The second context manager simply opens the first device in the list. 

The Spectran V6 uses a tree-like configuration structure which is represented as nested dictionaries in Python. The configuration is loaded one-by-one by walking through the dict recursively. That means the chronological order matters since the spectran checks each config element! For example if you want to use a low centerfrequency you have to bypass the rffilter. Otherwise, you might get an error.

After starting (and therewith connecting to) the device, packets can be received. The packets structure resembles the packet struct of the API.

The configuration can also be read from the device as follows:

```
with open('conf.json', 'w') as file:
    json.dump(device.get_config(), file, indent=4)
```
The conf.json can in turn be used to configure the device.

### Numpy

The wrapper uses numpy, because it features a zero-copy ctypes structs casting, to extract the packet payload
```
packet = spectran.get_packet()
```

### Prerequisites

- Make sure Aaronia RTSA PRO is installed on your system. If the path differs from default, use the path parameter with the RTSAWrapper constructor to change it.
- Install requirements via pip: `pip install -r requirements.txt`