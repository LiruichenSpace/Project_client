# -*- coding:utf8 -*-
import socket
import threading

import network


class connection():
    def __init__(self,ip_addr,port):
        self.socket=None
        self.sock_lock=threading.Lock()
        self.ip_addr=ip_addr
        self.port=port
    def start_connection(self):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.socket.connect((self.ip_addr,self.port))
        except :
            pass
    def stop_connection(self):
        network.send_jpeg(self.socket, None)
        self.socket.close()
