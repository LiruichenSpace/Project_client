# -*- coding:utf8 -*-
import socket
import pickle
import struct

import cv2
import numpy as np


def stop_connection(s):
    s.close()

def send_object(s,obj):
    """
    :param s: socket对象
    :param obj: 准备发送的对象
    :return: 无
    """
    if obj is None:
        s.send(struct.pack('l', 0))
        return
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]
    result, imgencode = cv2.imencode('.jpg', obj, encode_param)
    #imgencode=bytes(imgencode.to_string(),encoding='utf-8')
    imgencode=np.array(imgencode).tostring()
    print(len(imgencode))
    data_len=struct.pack('l',len(imgencode))
    s.send(data_len)
    s.send(imgencode)
def send_sample(s,obj):
    """
    :param s: socket对象
    :param obj: 准备发送的对象，结构为字典{‘pos’:(横坐标，纵坐标)，‘HR’:高清部分，‘LR':低清部分}训练的时候根据收到的sample块重建训练
    :return: 无
    """
    data=pickle.dumps(obj)
    print(len(data))
    data_len=struct.pack('l',-len(data))
    s.send(data_len)
    s.send(data)