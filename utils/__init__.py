# -*- coding:utf8 -*-

import logging
import os
from datetime import datetime

import cv2
import numpy as np


def get_timestamp():
    return datetime.now().strftime('%y%m%d-%H%M%S')

def setup_logger(logger_name, tofile=False,file_name='test',root='./logs',screen=True, level=logging.INFO):
    '''设定logger'''
    lg = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                                  datefmt='%y-%m-%d %H:%M:%S')
    lg.setLevel(level)
    if tofile:
        log_file = os.path.join(root, '{}_{}.log'.format(file_name,get_timestamp()))
        fh = logging.FileHandler(log_file, mode='w')
        fh.setFormatter(formatter)
        lg.addHandler(fh)
    if screen:
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        lg.addHandler(sh)
    return lg

def encode_jpeg(obj):
    """
    给定一个图像tensor，返回压缩后的jpeg格式字符串用于传输
    :param obj:待压缩的图像
    :return:编码后的字符串
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
    result, imgencode = cv2.imencode('.jpg', obj, encode_param)
    # imgencode=bytes(imgencode.to_string(),encoding='utf-8')
    return np.array(imgencode).tostring()
