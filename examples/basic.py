import rtsa_py_wrapper as rpw
import json

LINE_CLEAR = '\x1b[2K'
LINE_UP = '\033[1A'

with rpw.RTSAWrapper(rpw.AARTSAAPI_Wrapper_MemoryMode.MEDIUM) as wrapper:
    devices = wrapper.get_all_devices()
    with wrapper.instantiate_device(devices[0], rpw.AARTSAAPI_Wrapper_DeviceMode.IQRECEIVER) as spectran:
        spectran.connect()

        root = {
            'calibration': {
                'rffilter': { 'value': 'Bypass'},
                'preamp': { 'value': 'Preamp' },
            },
            'main': {
                'centerfreq': { 'value': 64_000_000 },
                'reflevel': { 'value': -20.0 },
            },
            'device': {
                'outputformat': { 'value': "iq" },
                'triggeredge': { 'value': "High" },
                'triggerflag': { 'value': "C0" },
            }
        }
        spectran.push_config(root)
        root = spectran.get_config()
        with open("conf.json", "w") as file:
            json.dump(root, file, indent=4)

        spectran.start()
        print(rpw.AARTSAAPI_Packet.get_header())
        # packet = spectran.get_packet()
        # last_packet_end_time = packet.endTime
        while True:
            packet = spectran.get_packet()
            # time_lost = packet.startTime - last_packet_end_time
            # print(time_lost)
            # print(LINE_UP, end=LINE_CLEAR)
            print(packet)

