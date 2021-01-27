# -*- coding:utf8 -*-
import logging
import socket
import pickle
import struct
import utils
import cv2
import numpy as np


def stop_connection(s):
    s.close()

def recvall(sock, count):
    """
    由于recv函数可能不会返回等于参数大小的内容，需要不断接收确保接收到了足够长的内容
    :param sock: socket对象
    :param count: 需要接受的字节数
    :return: 返回等于count大小的缓冲区
    """
    buf = b''  # buf是一个byte类型
    while count:
        # 接受TCP套接字的数据。数据以字符串形式返回，count指定要接收的最大数据量.
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def send_object(s,obj):
    """
    :param s: socket对象
    :param obj: 准备发送的对象
    :return: 无
    """
    logger=logging.getLogger('base')
    if obj is None:
        s.send(struct.pack('l', 0))
        return
    imgencode=utils.encode_jpeg(obj)
    logger.info(len(imgencode))
    data_len=struct.pack('l',len(imgencode))
    s.send(data_len)
    s.send(imgencode)
def send_sample(s,obj):
    """
    :param s: socket对象
    :param obj: 准备发送的对象，结构为字典{‘GT’:高清列表，‘LQs':低清列表}训练的时候根据收到的sample块重建训练
    :return: 无
    """
    data=pickle.dumps(obj)
    #print(len(data))
    #print(data)
    data_len=struct.pack('l',-len(data))
    s.send(data_len)
    s.send(data)