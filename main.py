# -*- coding:utf8 -*-
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import logging
import os
import os.path as osp
import pickle
import threading
import time
from pathlib import Path

import dataprocess
import network
from dataprocess.dataCapture import captureBuffer
from network.Connection import connection
from dataprocess.Sampler import TestSampler
import utils


def sample_thread(sock,capture_pool):
    sampler=TestSampler()
    logger=logging.getLogger('base')
    cnt=0
    while cnt<20:
        with capture_pool.pool_lock:
            if capture_pool.pool:
                sample_list,scaled=sampler.sample_and_filter(capture_pool.pool.pop())
                network.send_jpeg(sock,scaled)
                for sample in sample_list:
                    network.send_sample(sock,sample)
                cnt=cnt+1
                logger.info(cnt)
            else:
                time.sleep(0.02)

def create_datafile(file_path):
    """
    创建模拟服务端使用的pkl文件
    """
    logger = logging.getLogger('base')
    logger.info('create_datafile')
    capture_pool = captureBuffer()
    #capture_pool.create_datafile(file_path)
    capture_pool.create_PSNR_testfile(file_path)
    capture_pool.terminate = True

def start_client_no_block(ip_addr,port):
    """
    不使用多线程采集，单线程处理图像获取，直接使用多线程遇到了死锁问题
    """
    logger = logging.getLogger('base')
    logger.info('start_client')
    conn = connection(ip_addr, port)
    conn.start_connection()
    capture_pool = captureBuffer()
    capture_pool.start_capture_no_bolck(conn.socket)
    capture_pool.terminate = True
    conn.stop_connection()

def start_client_with_file(ip_addr,port,file_path):
    """
    利用pkl文件来模拟服务端的数据采集
    :param ip_addr: 服务端的ip地址
    :param port: 服务器端口
    :param file_path: 待使用的pkl文件位置
    """
    logger = logging.getLogger('base')
    logger.info('start_client')
    fp=open(file_path,'rb')
    conn = connection(ip_addr, port)
    conn.start_connection()
    while True:
        try:
            data = pickle.load(fp)
            if isinstance(data,dict):
                network.send_sample(conn.socket,data)
            else:
                network.send_jpeg(conn.socket,data)
        except EOFError:
            break
    conn.stop_connection()
    fp.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_filename',type=str,default=None)
    parser.add_argument('--out_file',type=str,default=None)
    parser.add_argument('--in_file',type=str,default=None)
    args=parser.parse_args()
    if not (args.log_filename is None):
        logger=utils.setup_logger('base',True,args.log_filename)
    else: 
        logger = utils.setup_logger('base', False)
    if not(args.in_file is None):
        if Path(args.in_file).is_file():
            start_client_with_file('192.168.137.1', 11111,args.in_file)
        else:
            logger.error(args.in_file + ' is not a valid file')
    elif not(args.out_file is None):
        create_datafile(args.out_file)
    else:
        start_client_no_block('192.168.137.1', 11111)


