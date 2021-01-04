import socket
import pickle
import struct


def start_connection(ip_addr,port):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((ip_addr,port))
    return s

def stop_connection(s):
    s.close()

def send_object(s,obj):
    """
    :param s: socket对象
    :param obj: 准备发送的对象
    :return: 无
    """
    if not obj:
        s.send(struct.pack('l', 0))
        return
    data=pickle.dumps(obj)
    data_len=struct.pack('l',len(data))
    s.send(data_len)
    s.send(data)
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