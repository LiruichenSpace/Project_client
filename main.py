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
                img=capture_pool.pool.pop()
                sample_list,scaled=sampler.sample_and_filter(img)
                obj={'img':utils.encode_img(scaled),'shape':img.shape,'sample':False}
                network.send_obj(sock,obj)
                for sample in sample_list:
                    network.send_obj(sock, sample)
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
    capture_pool.create_datafile(file_path)
    #capture_pool.create_PSNR_testfile(file_path)
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
    cnt = 0
    sampler=dataprocess.Sampler.TestSampler()
    start = time.time()
    while True:
        try:
            data = pickle.load(fp)
            data=utils.decode_jpeg(data)
            sample_list, scaled = sampler.sample_and_filter(data)
            obj = {'img': utils.encode_img(scaled), 'shape': data.shape, 'sample': False}
            network.send_obj(conn.socket, obj)
            for sample in sample_list:
                network.send_obj(conn.socket, sample)
            # TODO:考虑还有没有优化的策略
            cnt = cnt + 1
            if cnt % 10 == 0:
                curr_time = time.time()
                logger.info("sent {} frames in {} sec,fps:{}".format(cnt, curr_time - start,
                                                                          cnt / (curr_time - start)))
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
            start_client_with_file('192.168.0.100', 11111,args.in_file)
        else:
            logger.error(args.in_file + ' is not a valid file')
    elif not(args.out_file is None):
        create_datafile(args.out_file)
    else:
        start_client_no_block('192.168.0.100', 11111)
