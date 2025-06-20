# rtsa-python-wrapper

A Python wrapper module for the aaronia RTSA API

The module is based on the C++-Wrapper from the Aaronia-open-source library and provides similar functionality. It requires a Linux system and the Aaronia RTSA PRO Software.

## Warning

The use of this software is at your own risk. We accept no responsibility or compensation for any damage arising from its use.

## Getting Started

### Basic Usage

The wrapper should be used with context managers and uses 2 Classes that resemble the functionality of the API. Here is a basic example.
```python=
import rtsa-python-wrapper as rpw

with rpw.RTSAWrapper(rpw.AARTSAAPI_Wrapper_MemoryMode.MEDIUM) as wrapper:
    devices = wrapper.get_all_devices()
    with wrapper.instantiate_device(devices[0], rpw.AARTSAAPI_Wrapper_DeviceMode.RAW) as device:
        device.start()
        packet = device.get_packet()
```

The RTSAWrapper-Class features the functionality of handling the API and the devices connected to your computer. With calling `instantiate_device(device, DeviceMode)` we get an instance of the DeviceWrapper-Class that handles all the functionality that are specific to a device. See rtsa-python-wrapper.py for more information about all structs and functions of the API. 
After the start and the associated connection to the device, packets can be received. The packet struct members can be accessed like object variables, e.g. `packet.num`.

### Device Configuration

```python=
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
```

The Spectran V6 uses a tree-like configuration structure that we resemble as nested dictionaries. The configuration is loaded one-after-another by walking through the dict recursively. That means the chronological order inside the config dict matters! For example, to use a low centerfrequency you have to bypass the rffilter and/or reduce decimation first. Otherwise, you might get an error.

For review purposes, the configuration can also be read from the device as follows:

```
with open('conf.json', 'w') as file:
    json.dump(device.get_config(), file, indent=4)
```
The conf.json can also be pushed to the device.

### Receive Packet Data As Numpy Arrays

To extract the packet payload you can use the `get_sample_as_ndarray()` that internally casts the data as numpy array without copying it.
```
packet_data = packet.get_sample_as_ndarray()
```

### Prerequisites

- Make sure Aaronia RTSA PRO is installed on your system. If the path differs from default, use the path parameter with the RTSAWrapper constructor to change it.
- Install requirements via pip: `pip install -r requirements.txt`
