import logging
import pickle
import struct
import threading
import network

class SRHandler(threading.Thread):
    #TODO：读取发回的信息，按照某种规则修改采样器的采样率
    def __init__(self,sock,sampler):
        super().__init__()
        self.socket=sock
        self.sampler=sampler
        self.logger = logging.getLogger('base')
    def run(self) -> None:
        while True:
            data_len = network.recvall(self.socket, struct.calcsize('l'))
            data_len = struct.unpack('l', data_len)[0]
            obj=network.recvall(self.socket,data_len)
            obj=pickle.loads(obj)
            self.update_SR(obj)
    def update_SR(self,obj):
        self.logger.info(obj)