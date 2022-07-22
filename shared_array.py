import numpy as np
from multiprocessing import shared_memory


class sharedArrayHandle:
    def __init__(self, name, shape, dtype):
        self.name = name
        self.shape = shape
        self.dtype = dtype

class sharedArray:
    def __init__(self, handle_or_shape = [], dtype = float, name = ''):
        '''
        initialize a shared array
        input:
            1 input:
                handle: sharedArrayHandle object (attributes: name, shape, dtype)
            or 3 inputs
                shape: tuple of ints
                name: string
                dtype: any valid numpy dtype
        '''
        if type(handle_or_shape) == sharedArrayHandle: #  has handle [name, shape, dtype]
            handle = handle_or_shape
            self.handle = handle
            self.shm = shared_memory.SharedMemory(name = handle.name)
        else:
            shape = handle_or_shape
            if name == '': # declare space and get name
                size = np.prod(shape)*np.dtype(dtype).itemsize
                self.shm = shared_memory.SharedMemory(create=True, size=size)
                name = self.shm.name
            else:
                self.shm = shared_memory.SharedMemory(name = name)
            self.handle = sharedArrayHandle(name, shape, dtype)
        self.array = np.ndarray(shape = self.handle.shape, dtype=self.handle.dtype, buffer=self.shm.buf)
        
    def close(self):
        '''
        should be called when process is done with the shared array
        '''
        try:
            del self.array
            self.shm.close()
        except AttributeError:
            raise RuntimeError('#### sharedArray already closed!')
            
    def unlink(self):
        '''
        should be called when all processes are done with array (have called close())
        clears memory
        '''
        self.shm.unlink()
        
    def __getitem__(self,tup):
        try:
            return self.array[tup]
        except AttributeError:
            raise RuntimeError('#### sharedArray already closed!')
            
    def __setitem__(self, tup, val):
        try:
            self.array[tup] = val
        except AttributeError:
            raise RuntimeError('#### sharedArray already closed!')
            