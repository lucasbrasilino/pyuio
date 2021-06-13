from os import listdir
from glob import glob
import mmap

SYSFS_PATH = "/sys/class/uio"
MAP_SIZE = 65536

class UIODev(object):
    _memmap = None
    _dev = None
    _inst_name = None
    _sysfs_path = None

    def __init__(self,dev):

        if type(dev) is str:
            if len(dev) < 4:
                raise ValueError('device must be in format uioX')
            dev = int(dev[3:])
        if type(dev) is not int:
            raise ValueError('uio device must be string or integer')
        devnum = dev        
        self._sysfs_path = f'{SYSFS_PATH}/uio{devnum}'
        self._dev = f'/dev/uio{devnum}'
        self.__mmap()
        if self._memmap is None:
            return None
        self._inst_name = self.__get_inst_name()
    
    def __mmap(self):
        _fp = open(self._dev,"r+b")
        try:
            self._memmap = mmap.mmap(_fp.fileno(),MAP_SIZE,access=mmap.ACCESS_WRITE)
        except OSError:
            self._memmap = None
        _fp.close()
    
    def write_offset(self, offset, val, byteorder='little'):
        self.__offset_sanity_check(offset)
        if type(val) is str:
            if len(val) > 4:
                raise ValueError('String longer than 4 chars')
            data = bytes(val,encoding='utf8')
        elif type (val) is int:
            data = val.to_bytes(4,byteorder=byteorder)
        elif type(val) is not bytes:
            raise ValueError('Data in from a invalid type')
        elif len(bytes) > 4:
            raise ValueError('Data must be 32-bit wide')
        self._memmap.seek(offset)
        self._memmap.write(data)

    def write_idx(self,idx,val,byteorder='little'):
        if type(idx) is not int:
            raise ValueError('idx not integer')
        offset = idx << 2
        self.write_offset(offset,val,byteorder=byteorder)

    def read_offset(self,offset,byteorder='little'):
        self.__offset_sanity_check(offset)
        self._memmap.seek(offset)
        data = self._memmap.read(4)
        return int.from_bytes(data,byteorder=byteorder)

    def read_idx(self,idx,byteorder='little'):
        if type(idx) is not int:
            raise ValueError('idx not integer')
        offset = idx << 2
        return self.read_offset(offset)

    def __get_inst_name(self):
        _fp = open(f'{self._sysfs_path}/name','r')
        _content = _fp.readline()[:-1]
        _fp.close()
        return _content


    def __offset_sanity_check(self,offset):
        if type(offset) is not int:
            raise ValueError('offset must be an integer')
        if offset < 0 or offset > (MAP_SIZE-1):
            raise ValueError('index out or range')
        if offset % 4:
            raise ValueError('offset must be 32-bit aligned')

class UIODevices(object):
    _devices = {}

    def __init__(self):
        for d in glob(f'{SYSFS_PATH}/uio*') :
            _dev_sysfs_name = d.split('/')[-1:][0]
            _uio_device = UIODev(_dev_sysfs_name)
            if _uio_device._memmap is None:
                continue
            self._devices[_dev_sysfs_name] = _uio_device
            self._devices[_uio_device._inst_name] = _uio_device
        self.__dict__.update(self._devices)

    def __getitem__(self,idx):
        return self._devices[idx]

    # _devices holds both sysfs device name AND instance name
    def __len__(self):
        return int(len(self._devices)/2)