# -*- coding:utf8 -*-
import datetime
import logging
import os
import cv2
import numpy as np


def get_timestamp():
    return datetime.now().strftime('%y%m%d-%H%M%S')

def setup_logger(logger_name, root='./logs', level=logging.INFO, screen=False, tofile=False):
    '''set up logger'''
    lg = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s',
                                  datefmt='%y-%m-%d %H:%M:%S')
    lg.setLevel(level)
    if tofile:
        log_file = os.path.join(root,'{}.log'.format(get_timestamp()))
        fh = logging.FileHandler(log_file, mode='w')
        fh.setFormatter(formatter)
        lg.addHandler(fh)
    if screen:
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        lg.addHandler(sh)

def encode_jpeg(obj):
    """
    给定一个图像tensor，返回压缩后的jpeg格式字符串用于传输
    :param obj:
    :return:
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 15]
    result, imgencode = cv2.imencode('.jpg', obj, encode_param)
    # imgencode=bytes(imgencode.to_string(),encoding='utf-8')
    return np.array(imgencode).tostring()