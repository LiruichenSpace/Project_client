# -*- coding:utf8 -*-
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import os.path as osp
import threading
import time

import dataprocess
import network
from dataprocess.dataCapture import captureBuffer
from network.Connection import connection


def start_client(ip_addr,port):
    print('start_client')
    test_folder='./test_cv2_file'
    conn=connection(ip_addr,port)
    conn.start_connection()
    capture_pool=captureBuffer()
    capture_thread=threading.Thread(target=capture_pool.start_capture,args=())
    capture_thread.setDaemon(True)
    capture_thread.start()
    if not osp.exists(test_folder):
        os.makedirs(test_folder)
    # for i in range(10):
    #     #cv=dataprocess.get_cv_object(camera)
    #     obj='test_obj'
    #     network.send_sample(conn.socket,obj)
    #     #pickle.dump(cv,osp.join(test_folder,'{}.pkl'.format(i)))
    cnt=0
    while cnt<20:
        with capture_pool.pool_lock:
            if capture_pool.pool:
                network.send_object(conn.socket,capture_pool.pool.pop())
                cnt=cnt+1
                print(cnt)
            else:
                time.sleep(0.02)
    capture_pool.terminate=True
    conn.stop_connection()


if __name__ == '__main__':
    start_client('192.168.137.1',11111)


