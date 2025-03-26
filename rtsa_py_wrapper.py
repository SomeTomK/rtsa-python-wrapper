#!/usr/bin/env python

import ctypes, sys, time
import numpy as np
from typing import Self
from ctypes import c_int, c_uint64, c_int64, c_uint32, c_int32, c_double, c_float, c_wchar, c_wchar_p, c_void_p, c_bool, POINTER, pointer, Structure, sizeof
from enum import IntEnum

# Enumerations

class PrintIntEnum(IntEnum):
    def __str__(self) -> str:
        return f"{self.name}"

class AARTSAAPI_Result(PrintIntEnum):
    OK                          = 0x00000000
    EMPTY                       = 0x00000001
    RETRY                       = 0x00000002

    IDLE                        = 0x10000000
    CONNECTING                  = 0x10000001
    CONNECTED                   = 0x10000002
    STARTING                    = 0x10000003
    RUNNING                     = 0x10000004
    STOPPING                    = 0x10000005
    DISCONNECTING               = 0x10000006

    WARNING                     = 0x40000000
    WARNING_VALUE_ADJUSTED      = 0x40000001
    WARNING_VALUE_DISABLED      = 0x40000002

    ERROR                       = 0x80000000
    ERROR_NOT_INITIALIZED       = 0x80000001
    ERROR_NOT_FOUND             = 0x80000002
    ERROR_BUSY                  = 0x80000003
    ERROR_NOT_OPEN              = 0x80000004
    ERROR_NOT_CONNECTED         = 0x80000005
    ERROR_INVALID_CONFIG        = 0x80000006
    ERROR_BUFFER_SIZE           = 0x80000007
    ERROR_INVALID_CHANNEL       = 0x80000008
    ERROR_INVALID_PARAMETER     = 0x80000009
    ERROR_INVALID_SIZE          = 0x8000000a
    ERROR_MISSING_PATHS_FILE    = 0x8000000b
    ERROR_VALUE_INVALID         = 0x8000000c
    ERROR_VALUE_MALFORMED       = 0x8000000d

class AARTSAAPI_ConfigType(PrintIntEnum):
    OTHER                       = 0
    GROUP                       = 1
    BLOB                        = 2
    NUMBER                      = 3
    BOOL                        = 4
    ENUM                        = 5
    STRING                      = 6

class AARTSAAPI_Wrapper_DeviceType(PrintIntEnum):
    SPECTRANV6                  = 0

class AARTSAAPI_Wrapper_DeviceMode(PrintIntEnum):
    RAW                         = 0
    RTSA                        = 1
    SWEEPSA                     = 2
    IQRECEIVER                  = 3
    IQTRANSMITTER               = 4
    IQTRANSCEIVER               = 5

class AARTSAAPI_Wrapper_MemoryMode(PrintIntEnum):
    SMALL                       = 0
    MEDIUM                      = 1
    LARGE                       = 2
    LUDICRIOUS                  = 3

class AARTSAAPT_Trigger(PrintIntEnum):
    C0                          = 0x1000_0000 # TODO find out bitmask of other trigger flags


# Structs

class AARTSAAPI_Handle(Structure):
    _fields_ = [
            ("d", c_void_p)]

class AARTSAAPI_Device(Structure):
    _fields_ = [
            ("d", c_void_p)]

class AARTSAAPI_DeviceInfo(Structure):
    _fields_ = [
            ("cbsize", c_int64),

            ("serialNumber", c_wchar * 120),
            ("ready", c_bool),
            ("boost", c_bool),
            ("superspeed", c_bool),
            ("active", c_bool)]

class AARTSAAPI_Config(Structure):
    _fields_ = [
            ("d", c_void_p)]

class AARTSAAPI_ConfigInfo(Structure):
    _fields_ = [
            ("cbsize", c_int64),

            ("name", c_wchar * 80),
            ("title", c_wchar * 120),
            ("type", c_int),        # AARTSAAPI_ConfigType Enumeration
            ("minValue", c_double),
            ("maxValue", c_double),
            ("stepValue", c_double),
            ("unit", c_wchar * 10),
            ("options", c_wchar * 1000),
            ("disabledOptions", c_int64)]

class AARTSAAPI_Packet(Structure):
    _fields_ = [
            ("cbsize", c_int64),

            ("streamID", c_uint64),
            ("flags", c_uint64),

            ("startTime", c_double),
            ("endTime", c_double),
            ("startFrequency", c_double),
            ("stepFrequency", c_double),
            ("spanFrequency", c_double),
            ("rbwFrequency", c_double),

            ("num", c_int64),
            ("total", c_int64),
            ("size", c_int64),
            ("stride", c_int64),
            ("fp32", POINTER(c_float)),

            ("interleave", c_int64)]
    
    @staticmethod
    def get_header():
        header =  "| {:>16s} | {:>16s} | {:>16s} | {:>16s} | {:>16s} | {:>16s} | {:>16s} | {:>6s} | {:>6s} | {:>6s} |".format(
            "Flags",
            "startTime",
            "endTime",
            "startFrequency",
            "stepFrequency",
            "spanFrequency",
            "rbwFrequency",
            "num",
            "total",
            "stride"
        )
        return header + "\n" + "="*len(header)
    
    def __str__(self):
        return "| {:>16x} | {:>16.5f} | {:>16.5f} | {:>16.5f} | {:>16.5f} | {:>16.5f} | {:>16.5f} | {:>6n} | {:>6n} | {:>6n} |".format(
            self.flags,
            self.startTime,
            self.endTime,
            self.startFrequency,
            self.stepFrequency,
            self.spanFrequency,
            self.rbwFrequency,
            self.num,
            self.total,
            self.stride
        )
    
    def get_sample_as_ndarray(self) -> np.ndarray:
        # return [[self.fp32[n*packet.size + s] for s in range(self.stride)] for n in range(self.num)]
        # return self.fp32[:packet.size*packet.num]
        return np.ctypeslib.as_array(self.fp32, (self.num, self.size))


# Functions

def struct_copy(src):
    """Makes a copy of the src Struct and returns it"""
    dst = type(src)()
    pointer(dst)[0] = src
    return dst

def api(path="/opt/aaronia-rtsa-suite/Aaronia-RTSA-Suite-PRO/libAaroniaRTSAAPI.so"):

    librtsaapi = ctypes.CDLL(path)

    librtsaapi.AARTSAAPI_Init.argtypes = [c_uint32]
    librtsaapi.AARTSAAPI_Init.restype = c_uint32

    librtsaapi.AARTSAAPI_Shutdown.argtypes = []
    librtsaapi.AARTSAAPI_Shutdown.restype = c_uint32

    librtsaapi.AARTSAAPI_Version.argtypes = []
    librtsaapi.AARTSAAPI_Version.restype = c_uint32

    librtsaapi.AARTSAAPI_Open.argtypes = [POINTER(AARTSAAPI_Handle)]
    librtsaapi.AARTSAAPI_Open.restype = c_uint32

    librtsaapi.AARTSAAPI_Close.argtypes = [POINTER(AARTSAAPI_Handle)]
    librtsaapi.AARTSAAPI_Close.restype = c_uint32

    librtsaapi.AARTSAAPI_RescanDevices.argtypes = [POINTER(AARTSAAPI_Handle), c_int32]
    librtsaapi.AARTSAAPI_RescanDevices.restype = c_uint32

    librtsaapi.AARTSAAPI_ResetDevices.argtypes = [POINTER(AARTSAAPI_Handle)]
    librtsaapi.AARTSAAPI_ResetDevices.restype = c_uint32

    librtsaapi.AARTSAAPI_EnumDevice.argtypes = [POINTER(AARTSAAPI_Handle), c_wchar_p, c_int32, ctypes.c_void_p]
    librtsaapi.AARTSAAPI_EnumDevice.restype = c_uint32

    librtsaapi.AARTSAAPI_OpenDevice.argtypes = [POINTER(AARTSAAPI_Handle), POINTER(AARTSAAPI_Device), c_wchar_p, c_wchar_p]
    librtsaapi.AARTSAAPI_OpenDevice.restype = c_uint32

    librtsaapi.AARTSAAPI_CloseDevice.argtypes = [POINTER(AARTSAAPI_Handle), POINTER(AARTSAAPI_Device)]
    librtsaapi.AARTSAAPI_CloseDevice.restype = c_uint32

    librtsaapi.AARTSAAPI_ConnectDevice.argtypes = [POINTER(AARTSAAPI_Device)]
    librtsaapi.AARTSAAPI_ConnectDevice.restype = c_uint32

    librtsaapi.AARTSAAPI_DisconnectDevice.argtypes = [POINTER(AARTSAAPI_Device)]
    librtsaapi.AARTSAAPI_DisconnectDevice.restype = c_uint32

    librtsaapi.AARTSAAPI_StartDevice.argtypes = [POINTER(AARTSAAPI_Device)]
    librtsaapi.AARTSAAPI_StartDevice.restype = c_uint32

    librtsaapi.AARTSAAPI_StopDevice.argtypes = [POINTER(AARTSAAPI_Device)]
    librtsaapi.AARTSAAPI_StopDevice.restype = c_uint32

    librtsaapi.AARTSAAPI_GetDeviceState.argtypes = [POINTER(AARTSAAPI_Device)]
    librtsaapi.AARTSAAPI_GetDeviceState.restype = c_uint32

    librtsaapi.AARTSAAPI_AvailPackets.argtypes = [POINTER(AARTSAAPI_Device), c_int32, POINTER(c_int32)]
    librtsaapi.AARTSAAPI_AvailPackets.restype = c_uint32

    librtsaapi.AARTSAAPI_GetPacket.argtypes = [POINTER(AARTSAAPI_Device), c_int32, c_int32, POINTER(AARTSAAPI_Packet)]
    librtsaapi.AARTSAAPI_GetPacket.restype = c_uint32

    librtsaapi.AARTSAAPI_ConsumePackets.argtypes = [POINTER(AARTSAAPI_Device), c_int32, c_int32]
    librtsaapi.AARTSAAPI_ConsumePackets.restype = c_uint32

    librtsaapi.AARTSAAPI_GetMasterStreamTime.argtypes = [POINTER(AARTSAAPI_Device), c_double]       # the second parameter has a & between type and its name. Don't know what that means
    librtsaapi.AARTSAAPI_GetMasterStreamTime.restype = c_uint32

    librtsaapi.AARTSAAPI_SendPacket.argtypes = [POINTER(AARTSAAPI_Device), c_int32, POINTER(AARTSAAPI_Packet)]
    librtsaapi.AARTSAAPI_SendPacket.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigRoot.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config)]
    librtsaapi.AARTSAAPI_ConfigRoot.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigHealth.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config)]
    librtsaapi.AARTSAAPI_ConfigHealth.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigFirst.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), POINTER(AARTSAAPI_Config)]
    librtsaapi.AARTSAAPI_ConfigFirst.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigNext.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), POINTER(AARTSAAPI_Config)]
    librtsaapi.AARTSAAPI_ConfigNext.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigFind.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), POINTER(AARTSAAPI_Config), c_wchar_p]
    librtsaapi.AARTSAAPI_ConfigFind.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigGetName.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), c_wchar_p]
    librtsaapi.AARTSAAPI_ConfigGetName.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigGetInfo.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), POINTER(AARTSAAPI_ConfigInfo)]
    librtsaapi.AARTSAAPI_ConfigGetInfo.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigSetFloat.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), c_double]
    librtsaapi.AARTSAAPI_ConfigSetFloat.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigGetFloat.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), POINTER(c_double)]
    librtsaapi.AARTSAAPI_ConfigGetFloat.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigSetString.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), c_wchar_p]
    librtsaapi.AARTSAAPI_ConfigSetString.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigGetString.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), c_wchar_p, POINTER(c_int64)]
    librtsaapi.AARTSAAPI_ConfigGetString.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigSetInteger.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), c_int64]
    librtsaapi.AARTSAAPI_ConfigSetInteger.restype = c_uint32

    librtsaapi.AARTSAAPI_ConfigGetInteger.argtypes = [POINTER(AARTSAAPI_Device), POINTER(AARTSAAPI_Config), POINTER(c_int64)]
    librtsaapi.AARTSAAPI_ConfigGetInteger.restype = c_uint32

    return librtsaapi


# Wrapper Classes

class DeviceWrapper:
    def __init__(self, 
                 librtsaapi, 
                 mAPTHandle, 
                 serialNumber, 
                 devMode, 
                 devType=AARTSAAPI_Wrapper_DeviceType.SPECTRANV6) -> None:
        self.__librtsaapi = librtsaapi
        self.__mAPIHandle = mAPTHandle
        self.__dHandle = AARTSAAPI_Device()
        self.__dpacket = AARTSAAPI_Packet()
        self.__dconfig = AARTSAAPI_Config()
        self.__serialNumber = serialNumber
        self.__devMode = devMode
        self.__devType = devType
        self.__isOpen = False
        self.__isConnected = False
        self.__isStarted = False

        self.__dHandle.cbsize = sizeof(self.__dHandle)
        self.__dpacket.cbsize = sizeof(self.__dpacket)

    def __enter__(self) -> Self:
        self.__device_open()
        self.__isOpen = True
        return self
    
    def __device_open(self) -> None:
        modeType = f"{self.__devType}/{self.__devMode}".lower()
        res = self.__librtsaapi.AARTSAAPI_OpenDevice(pointer(self.__mAPIHandle), 
                                                     pointer(self.__dHandle), 
                                                     modeType, 
                                                     self.__serialNumber)
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to open device: {AARTSAAPI_Result(res)}")
        
    def __device_close(self) -> None:
        self.__librtsaapi.AARTSAAPI_CloseDevice(pointer(self.__mAPIHandle), pointer(self.__dHandle))

    def __device_connect(self) -> None:
        res = self.__librtsaapi.AARTSAAPI_ConnectDevice(pointer(self.__dHandle))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to connect to device: {AARTSAAPI_Result(res)}")
        
    def __device_disconnect(self) -> None:
        self.__librtsaapi.AARTSAAPI_DisconnectDevice(pointer(self.__dHandle))

    def __device_start(self) -> None:
        res = self.__librtsaapi.AARTSAAPI_StartDevice(pointer(self.__dHandle))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to start device: {AARTSAAPI_Result(res)}")

    def __device_stop(self) -> None:
        self.__librtsaapi.AARTSAAPI_StopDevice(pointer(self.__dHandle))

    def __device_get_state(self) -> AARTSAAPI_Result:
        res = self.__librtsaapi.AARTSAAPI_GetDeviceState(pointer(self.__dHandle))
        # if return value not a state
        if not res & AARTSAAPI_Result.IDLE:
            raise RuntimeError(f"Failed to get device state: {AARTSAAPI_Result(res)}")
        return AARTSAAPI_Result(res)
    
    def __packet_available(self, channel: c_int32) -> int:
        num = c_int32()
        res = self.__librtsaapi.AARTSAAPI_AvailPackets(pointer(self.__dHandle), channel, pointer(num))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get available packet count on channel {channel}: {AARTSAAPI_Result(res)}")
        return num
    
    def __packet_consume(self, channel: c_int32, num: c_int32) -> None:
        res = self.__librtsaapi.AARTSAAPI_ConsumePackets(pointer(self.__dHandle), channel, num)
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to consume packet num {num} on channel {channel}: {AARTSAAPI_Result(res)}")
        return num

    
    def __packet_get(self, channel: c_int, index: c_int, packet: AARTSAAPI_Packet, wait_time) -> None:
        while True:
            res = self.__librtsaapi.AARTSAAPI_GetPacket(pointer(self.__dHandle), channel, index, pointer(packet))
            if res == AARTSAAPI_Result.EMPTY:
                if wait_time: time.sleep(wait_time/1000)
                continue
            elif res != AARTSAAPI_Result.OK:
                raise RuntimeError(f"Failed to get packet from channel {channel} with index {index}: {AARTSAAPI_Result(res)}")
            else:
                break

    def __config_root(self) -> AARTSAAPI_Config:
        config = AARTSAAPI_Config()
        res = self.__librtsaapi.AARTSAAPI_ConfigRoot(pointer(self.__dHandle), pointer(config))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get config root tree: {AARTSAAPI_Result(res)}")
        return config

    def __config_health(self) -> AARTSAAPI_Config:
        config = AARTSAAPI_Config()
        res = self.__librtsaapi.AARTSAAPI_ConfigHealth(pointer(self.__dHandle), pointer(config))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get config health tree: {AARTSAAPI_Result(res)}")
        return config

    def __config_first(self, group: AARTSAAPI_Config) -> AARTSAAPI_Config:
        config = AARTSAAPI_Config()
        res = self.__librtsaapi.AARTSAAPI_ConfigFirst(pointer(self.__dHandle), pointer(group), pointer(config))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get first child config: {AARTSAAPI_Result(res)}")
        return config
    
    def __config_next(self, group: AARTSAAPI_Config, config: AARTSAAPI_Config) -> AARTSAAPI_Result:
        return self.__librtsaapi.AARTSAAPI_ConfigNext(pointer(self.__dHandle), pointer(group), pointer(config))

    def __config_find(self, group: AARTSAAPI_Config, name: c_wchar_p) -> AARTSAAPI_Config:
        config = AARTSAAPI_Config()
        res = self.__librtsaapi.AARTSAAPI_ConfigFind(pointer(self.__dHandle), pointer(group), pointer(config), name)
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to find config at path {name}: {AARTSAAPI_Result(res)}")
        return config

    def __config_get_name(self, config: AARTSAAPI_Config) -> c_wchar_p:
        name = c_wchar() * 80
        res = self.__librtsaapi.AARTSAAPI_ConfigGetName(pointer(self.__dHandle), pointer(config), pointer(name))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get internal name of config: {AARTSAAPI_Result(res)}")
        return name

    def __config_get_info(self, config: AARTSAAPI_Config) -> AARTSAAPI_ConfigInfo:
        cinfo = AARTSAAPI_ConfigInfo()
        cinfo.cbsize = sizeof(cinfo)
        res = self.__librtsaapi.AARTSAAPI_ConfigGetInfo(pointer(self.__dHandle), pointer(config), pointer(cinfo))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get config info: {AARTSAAPI_Result(res)}")
        return cinfo

    def __config_set_float(self, config: AARTSAAPI_Config, value: c_double) -> None:
        res = self.__librtsaapi.AARTSAAPI_ConfigSetFloat(pointer(self.__dHandle), pointer(config), value)
        if res & AARTSAAPI_Result.ERROR:
            raise RuntimeError(f"Failed to set float {value} for config item \"{cinfo.name}\": {AARTSAAPI_Result(res)}")
        elif res & AARTSAAPI_Result.WARNING:
            cinfo = self.__config_get_info(config)
            print(f"Failed to set float {value} of config item \"{cinfo.name}\": {AARTSAAPI_Result(res)}", file=sys.stderr) # TODO has repetitions; no prints in module!

    def __config_get_float(self, config: AARTSAAPI_Config) -> float:
        ret = c_double()
        res = self.__librtsaapi.AARTSAAPI_ConfigGetFloat(pointer(self.__dHandle), pointer(config), pointer(ret))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get float: {AARTSAAPI_Result(res)}")
        return ret.value

    def __config_set_string(self, config: AARTSAAPI_Config, value: c_wchar_p) -> None:
        res = self.__librtsaapi.AARTSAAPI_ConfigSetString(pointer(self.__dHandle), pointer(config), value)
        cinfo = self.__config_get_info(config)
        if res & AARTSAAPI_Result.ERROR:
            raise RuntimeError(f"Failed to set string {value} for config item \"{cinfo.name}\": {AARTSAAPI_Result(res)}")
        elif res & AARTSAAPI_Result.WARNING:
            print(f"Failed to set string {value} of config item \"{cinfo.name}\": {AARTSAAPI_Result(res)}", file=sys.stderr)

    def __config_get_string(self, config: AARTSAAPI_Config) -> str:
        ret = (c_wchar * 1000)()
        size = c_int64(sizeof(ret))
        res = self.__librtsaapi.AARTSAAPI_ConfigGetString(pointer(self.__dHandle), pointer(config), ret, pointer(size))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get string: {AARTSAAPI_Result(res)}")
        return ret.value
    
    def __config_set_integer(self, config: AARTSAAPI_Config, value: c_int64) -> None:
        res = self.__librtsaapi.AARTSAAPI_ConfigSetInteger(pointer(self.__dHandle), pointer(config), value)
        cinfo = self.__config_get_info(config)
        if res & AARTSAAPI_Result.ERROR:
            raise RuntimeError(f"Failed to set integer {value} for config item \"{cinfo.name}\": {AARTSAAPI_Result(res)}")
        elif res & AARTSAAPI_Result.WARNING:
            print(f"WARNING: Failed to set integer {value} of config item \"{cinfo.name}\": {AARTSAAPI_Result(res)}", file=sys.stderr)

    def __config_get_integer(self, config: AARTSAAPI_Config) -> int:
        ret = c_int64()
        res = self.__librtsaapi.AARTSAAPI_ConfigGetInteger(pointer(self.__dHandle), pointer(config), pointer(ret))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get integer: {AARTSAAPI_Result(res)}")
        return ret.value

    def __config_get_bool(self, config: AARTSAAPI_Config) -> bool:
        ret = c_int64()
        res = self.__librtsaapi.AARTSAAPI_ConfigGetInteger(pointer(self.__dHandle), pointer(config), pointer(ret))
        # Config item might represent a button
        if res == AARTSAAPI_Result.ERROR_INVALID_CONFIG:
            return False
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to get integer: {AARTSAAPI_Result(res)}")
        return bool(ret.value)
        
    def __get_children(self, group: AARTSAAPI_Config) -> list[AARTSAAPI_Config]:
        cinfo = self.__config_get_info(group)
        if AARTSAAPI_ConfigType(cinfo.type) != AARTSAAPI_ConfigType.GROUP:
            raise RuntimeError(f"Cannot get children of non group config node {cinfo.name}: type {AARTSAAPI_ConfigType(cinfo.type)}")
        config_iterator = self.__config_first(group)
        children = [struct_copy(config_iterator)]
        while (self.__config_next(group, config_iterator) == AARTSAAPI_Result.OK):
            children.append(struct_copy(config_iterator))
        return children

    def __config_walk(self, config: AARTSAAPI_Config) -> dict:
        cinfo = self.__config_get_info(config)
        res = {}
        if cinfo.type == AARTSAAPI_ConfigType.GROUP:
            children = self.__get_children(config)
            for child in children:
                res.update(self.__config_walk(child))
        elif cinfo.type == AARTSAAPI_ConfigType.NUMBER:
            res["title"] = cinfo.title
            res["value"] = self.__config_get_float(config)
            res["unit"] = cinfo.unit
            res["type"] = str(AARTSAAPI_ConfigType(cinfo.type))
            res["minValue"] = cinfo.minValue
            res["maxValue"] = cinfo.maxValue
            res["stepValue"] = cinfo.stepValue
            res["disabledOptions"] = cinfo.disabledOptions
        elif cinfo.type == AARTSAAPI_ConfigType.BOOL:
            res["title"] = cinfo.title
            res["value"] = self.__config_get_bool(config)
            res["type"] = str(AARTSAAPI_ConfigType(cinfo.type))
            res["disabledOptions"] = cinfo.disabledOptions
        elif cinfo.type == AARTSAAPI_ConfigType.STRING:
            res["title"] = cinfo.title
            res["value"] = self.__config_get_string(config)
            res["type"] = str(AARTSAAPI_ConfigType(cinfo.type))
            res["disabledOptions"] = cinfo.disabledOptions
        elif cinfo.type == AARTSAAPI_ConfigType.ENUM:
            res["title"] = cinfo.title
            res["value"] = self.__config_get_string(config)
            res["options"] = cinfo.options
            res["type"] = str(AARTSAAPI_ConfigType(cinfo.type))
            res["disabledOptions"] = cinfo.disabledOptions
            pass
        else:
            raise RuntimeError(f"Unknown config type of enumeration value: {cinfo.type}")
        return {f"{cinfo.name}" : res}
    
    def __dict_to_paths(self, d: dict, parent_key=""):
        paths = []
        for k, v in d.items():
            new_key = f"{parent_key}/{k}" if parent_key else k
            if isinstance(v, dict) and isinstance(list(v.values())[0], dict):
                paths.extend(self.__dict_to_paths(v, new_key))
            elif isinstance(v, dict):
                paths.append((new_key, v["value"]))
        return paths

    def connect(self) -> None:
        if self.__isConnected:
            return
        if not self.__isOpen:
            raise RuntimeError(f"Failed to connect to device: Device not open!")
        self.__device_connect()
        self.__isConnected = True
        
    def start(self) -> None:
        if self.__isStarted:
            return
        if not self.__isConnected:
            self.connect()
        self.__device_start()
        self.__isStarted = True

    def wait_till_started(self) -> None:
        while True:
            res = self.__librtsaapi.AARTSAAPI_GetDeviceState(pointer(self.__dHandle))
            if res == AARTSAAPI_Result.RUNNING:
                break

    def stop(self) -> None:
        if self.__isStarted:
            self.__device_stop()
        self.__isStarted = False

    def disconnect(self) -> None:
        if self.__isConnected:
            self.__device_disconnect()
            self.__isConnected = False

    def get_device_state(self) -> str:
        res = self.__librtsaapi.AARTSAAPI_GetDeviceState(pointer(self.__dHandle))
        return str(AARTSAAPI_Result(res))

    def available_packets(self, channel=0) -> int:
        return self.__packet_available(channel).value
    
    def get_packet(self, channel=0, wait_time=0, new=False) -> AARTSAAPI_Packet:
        if new:
            packet = self.__dpacket
        else:
            packet = AARTSAAPI_Packet()
            packet.cbsize = sizeof(packet)
        self.__packet_get(channel, 0, packet, wait_time)
        self.__packet_consume(channel, 1)
        return packet
            
    def flush_channel(self, channel=0) -> None:
        num = self.__packet_available(channel)
        self.__packet_consume(channel, num)

    def push_config(self, tree: dict):
        if 'calibration' in tree and 'calibrationreload' in tree['calibration']:
            # We get an Error if this is set
            del tree['calibration']['calibrationreload']
        paths = self.__dict_to_paths(tree)
        root = self.__config_root()
        for path, value in paths:
            config = self.__config_find(root, path)
            cinfo = self.__config_get_info(config)
            if cinfo.type == AARTSAAPI_ConfigType.NUMBER:
                self.__config_set_float(config, value)
            elif cinfo.type == AARTSAAPI_ConfigType.BOOL:
                self.__config_set_integer(config, int(value))
            elif cinfo.type == AARTSAAPI_ConfigType.STRING:
                self.__config_set_string(config, value)
            elif cinfo.type == AARTSAAPI_ConfigType.ENUM:
                self.__config_set_string(config, value)
            else:
                raise RuntimeError(f"Failed to deploy config item {cinfo.name} of unsupported type: {AARTSAAPI_ConfigType(cinfo.type)}")
            
    def get_config(self) -> dict:
        root = self.__config_root()
        return self.__config_walk(root)['root']

    def get_health(self) -> dict:
        health = self.__config_health()
        return self.__config_walk(health)['health']

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.stop()
        self.disconnect()
        if self.__isOpen:
            self.__device_close()


class RTSAWrapper:

    def __init__(self, memoryMode: AARTSAAPI_Wrapper_MemoryMode) -> None:
        self.__librtsaapi = api()
        self.__mAPIHandle = None
        self.__mDevices = None
        self.memoryMode = memoryMode

    def __enter__(self) -> Self:
        self.__mAPIHandle = AARTSAAPI_Handle()
        self.__api_init()
        self.__api_open()
        return self
    
    def __api_init(self) -> None:
        res = self.__librtsaapi.AARTSAAPI_Init(self.memoryMode)
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed in initialize RTSAAPI: {AARTSAAPI_Result(res)}")
        
    def __api_shutdown(self) -> None:
        self.__librtsaapi.AARTSAAPI_Shutdown()

    def __api_version(self) -> int:
        return self.__librtsaapi.AARTSAAPI_Version()
    
    def __api_open(self) -> None:
        res = self.__librtsaapi.AARTSAAPI_Open(pointer(self.__mAPIHandle))
        if res != AARTSAAPI_Result.OK:
            self.__api_shutdown()
            raise RuntimeError(f"Failed to open AARTSAAPI library handle: {AARTSAAPI_Result(res)}")

    def __api_close(self) -> None:
        self.__librtsaapi.AARTSAAPI_Close(pointer(self.__mAPIHandle))

    def __api_rescan_devices(self, timeout) -> None:
        res = AARTSAAPI_Result.RETRY
        while res == AARTSAAPI_Result.RETRY:
            res = self.__librtsaapi.AARTSAAPI_RescanDevices(pointer(self.__mAPIHandle), timeout)
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed to scan for devices: {AARTSAAPI_Result(res)}")
        
    def __api_reset_devices(self) -> None:
        res = self.__librtsaapi.AARTSAAPI_ResetDevices(pointer(self.__mAPIHandle))
        if res != AARTSAAPI_Result.OK:
            raise RuntimeError(f"Failed in reset devices: {AARTSAAPI_Result(res)}")
                                                       
        
    def __api_enum_device(self, devType, i, dinfo) -> AARTSAAPI_Result:
        return self.__librtsaapi.AARTSAAPI_EnumDevice(
                pointer(self.__mAPIHandle), str(devType).lower(), i, pointer(dinfo))

    def get_all_devices(self, devType=AARTSAAPI_Wrapper_DeviceType.SPECTRANV6, timeout=2000) -> list:
        self.__mDevices = []
        self.__api_rescan_devices(timeout)
        res = AARTSAAPI_Result.OK
        i = 0

        # loop through devices to get device info of all
        while res == AARTSAAPI_Result.OK:
            dinfo = AARTSAAPI_DeviceInfo(cbsize=sizeof(AARTSAAPI_DeviceInfo))
            res = self.__api_enum_device(devType, i, dinfo)
            if res == AARTSAAPI_Result.OK:
                self.__mDevices.append(dinfo)
            i += 1
        return [device.serialNumber for device in self.__mDevices]

    def instantiate_device(self, 
                           serialNumber, 
                           devMode, 
                           devType=AARTSAAPI_Wrapper_DeviceType.SPECTRANV6) -> DeviceWrapper:
        return DeviceWrapper(self.__librtsaapi, self.__mAPIHandle, serialNumber, devMode, devType)

    def get_Handle(self) -> AARTSAAPI_Handle:
        return self.__mAPIHandle

    def version(self) -> str:
        ver = self.__librtsaapi.AARTSAAPI_Version()
        return f"Version:{ver >> 16}, Revision:{ver & 0xFFFF}"

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.__api_close()
        self.__mAPIHandle = None
        self.__api_shutdown()