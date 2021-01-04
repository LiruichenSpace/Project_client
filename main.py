# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import os.path as osp
import pickle
import time
import network
import matplotlib.pyplot as plt

import dataprocess


def start_client(ip_addr,port):
    print('start_client')
    camera=dataprocess.start_camera()
    test_folder='./test_cv2_file'
    sock=network.start_connection(ip_addr,port)
    plt.figure()
    if not osp.exists(test_folder):
        os.makedirs(test_folder)
    for i in range(10):
        #cv=dataprocess.get_cv_object(camera)
        obj='test_obj'
        network.send_sample(sock,obj)
        #pickle.dump(cv,osp.join(test_folder,'{}.pkl'.format(i)))
    network.send_object(sock,None)

    network.stop_connection(sock)


if __name__ == '__main__':
    start_client('192.168.137.1',11111)


