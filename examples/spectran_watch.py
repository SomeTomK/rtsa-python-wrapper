import rtsa_py_wrapper as rpa
import time

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'

def main():
    with rpa.RTSAWrapper(rpa.AARTSAAPI_Wrapper_MemoryMode.LARGE) as wrapper:
        devices = wrapper.get_all_devices()
        with wrapper.instantiate_device(devices[0], rpa.AARTSAAPI_Wrapper_DeviceMode.IQRECEIVER) as spectran:
            spectran.start()
            while True:
                health = spectran.get_health()
                print(f"Rx1 IQ Sample/sec  {health['rx1iqsamplessecond']['value']}")
                print(f"Errors             {health['errors']['value']}")
                print(f"Errors/sec         {health['errorssecond']['value']}")
                print(f"USB Overflow/sec   {health['usboverflowssecond']['value']}")
                print(f"Main USB Bytes/sec {health['mainusbbytessecond']['value']}")
                for _ in range(5):
                    print(LINE_UP, end=LINE_CLEAR)
                time.sleep(0.1)

if __name__ == "__main__":
    main()