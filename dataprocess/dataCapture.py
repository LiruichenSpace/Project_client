# -*- coding:utf8 -*-
import logging
import threading
import time
import pickle
import os

#import cv2
from pathlib import Path

import matplotlib.pyplot as plt
import cv2
import numpy as np
import picamera
import utils
from picamera.array import PiRGBArray
from dataprocess.Sampler import TestSampler
from dataprocess.SRHandler import SRHandler


# 直接RGB解码可以获取到RGB格式，但是是（H，W，C）格式的tensor，需要进行调整
import network


class captureBuffer():
    """
    通过start_capture函数来开始，结果存于pool中，可以从中取得
    超过buffer长度的部分会被抛弃
    使用时需要通过pool_lock变量互斥访问
    通过将其变量terminate设为True来停止
    """

    def __init__(self):
        #self.pool_lock = threading.Lock()
        #self.pool = []
        self.count = 0
        #self.pool_size = 5
        self.terminate = False
        self.start = time.time()
        self.logger=logging.getLogger('base')
        self.sampler = TestSampler()
    def start_capture_no_bolck(self,sock):
        self.srhandler=SRHandler(sock,self.sampler)
        self.srhandler.setDaemon(True)
        self.srhandler.start()#开启接收线程
        with picamera.PiCamera() as camera:
            rawFrame = PiRGBArray(camera, (640, 480))
            camera.resolution = (640, 480)
            camera.framerate = 20 #目前能够到达17fps左右的采集速度，推测此前瓶颈在于网络传输，而，
            time.sleep(2)
            self.start = time.time()
            cnt=0
            start=time.time()
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                sample_list, scaled = self.sampler.sample_and_filter(np.array(frame.array, dtype=np.uint8))
                network.send_jpeg(sock, scaled)
                for sample in sample_list:
                    network.send_sample(sock, sample)
                cnt = cnt + 1
                if cnt%10:
                    self.logger.info("sent {} frames in {} sec,fps:{}".format(cnt, time.time() - start,
                                                                                 cnt / (time.time() - start)))
                if cnt>200:
                    break
                self.logger.info(cnt)
                self.count = self.count + 1
                rawFrame.seek(0)
                rawFrame.truncate()
                if self.terminate:
                    self.logger.info('terminate')
                    break
    def create_datafile(self,file_path):
        f_path=Path(file_path)
        if not f_path.parent.exists():
            f_path.parent.mkdir(parents=True)
        sampler=TestSampler()
        fp=open(file_path,'wb')
        with picamera.PiCamera() as camera:
            rawFrame = PiRGBArray(camera, (640, 480))
            camera.resolution = (640, 480)
            camera.framerate = 20
            time.sleep(2)
            self.start = time.time()
            cnt=0
            start=time.time()
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                sample_list, scaled = sampler.sample_and_filter(np.array(frame.array, dtype=np.uint8))
                pickle.dump(scaled,fp,-1)
                for sample in sample_list:
                    pickle.dump(sample,fp,-1)
                cnt = cnt + 1
                if cnt%10:
                    self.logger.info("sent {} frames in {} sec,fps:{}".format(cnt, time.time() - start,
                                                                                 cnt / (time.time() - start)))
                if cnt>200:
                    break
                self.logger.info(cnt)
                self.count = self.count + 1
                rawFrame.seek(0)
                rawFrame.truncate()
                if self.terminate:
                    self.logger.info('terminate')
                    break
        fp.close()
    def create_PSNR_testfile(self,file_path):
        f_path=Path(file_path)
        if not f_path.parent.exists():
            f_path.parent.mkdir(parents=True)
        sampler=TestSampler()
        fp=open(file_path,'wb')
        with picamera.PiCamera() as camera:
            rawFrame = PiRGBArray(camera, (640, 480))
            camera.resolution = (640, 480)
            camera.framerate = 20
            time.sleep(2)
            self.start = time.time()
            cnt=0
            start=time.time()
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                origin = np.array(frame.array, dtype=np.uint8)
                sample_list, scaled = sampler.sample_and_filter(origin)
                obj = {'origin': utils.encode_img(origin), 'scaled': utils.encode_img(scaled)}
                pickle.dump(obj, fp, -1)
                for sample in sample_list:
                    pickle.dump(sample,fp,-1)
                cnt = cnt + 1
                if cnt%10:
                    self.logger.info("sent {} frames in {} sec,fps:{}".format(cnt, time.time() - start,
                                                                                 cnt / (time.time() - start)))
                if cnt>200:
                    break
                self.logger.info(cnt)
                self.count = self.count + 1
                rawFrame.seek(0)
                rawFrame.truncate()
                if self.terminate:
                    self.logger.info('terminate')
                    break
        fp.close()
    def create_dataset_testfile(self,dir_path,out_path):
        subdir_list=os.listdir(dir_path)
        sampler=TestSampler()
        plt.ion()
        plt.figure(1)
        for name in subdir_list:
            self.logger.info('start process {}:'.format(name))
            cnt=0
            fp=open(os.path.join(out_path,str(name)+'.pkl'),'wb')
            img_namelist=os.listdir(os.path.join(dir_path,name))
            img_namelist= np.sort(img_namelist)
            for img in img_namelist:
                img_path=os.path.join(dir_path,name,img)
                img_data=cv2.imread(img_path,cv2.IMREAD_COLOR)
                img_data=cv2.resize(img_data,(640,480))
                plt.imshow(img_data)
                plt.draw()
                plt.show()
                #print(img_data.shape)
                #print(img_data)
                sample_list, scaled = sampler.sample_and_filter(img_data)
                obj = {'origin': utils.encode_img(img_data), 'scaled': utils.encode_img(scaled)}
                pickle.dump(obj, fp, -1)
                for sample in sample_list:
                    pickle.dump(sample, fp, -1)
                cnt = cnt + 1
                self.logger.info(cnt)
                self.count = self.count + 1
            fp.close()


if __name__ == '__main__':
    pass
