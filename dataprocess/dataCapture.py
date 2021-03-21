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
            camera.framerate = 15 #目前能够到达17fps左右的采集速度，推测此前瓶颈在于网络传输
            shape=(640,480)
            time.sleep(2)
            self.start = time.time()
            cnt=0
            start=self.start
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                frame=np.array(frame.array, dtype=np.uint8)
                sample_list, scaled = self.sampler.sample_and_filter(frame)
                obj={'img':utils.encode_img(scaled),'shape':shape,'sample':False}
                network.send_obj(sock,obj)
                for sample in sample_list:
                    network.send_obj(sock, sample)
                #TODO:考虑还有没有优化的策略
                cnt = cnt + 1
                if cnt%10==0:
                    curr_time=time.time()
                    self.logger.info("sent {} frames in {} sec,fps:{}".format(cnt, curr_time - start,
                                                                                 cnt / (curr_time - start)))
                if cnt>200:
                    self.logger.info('process end')
                    break
                #self.logger.info(cnt)
                self.count = self.count + 1
                rawFrame.seek(0)
                rawFrame.truncate()
                if self.terminate:
                    self.logger.info('terminate')
                    break
    def create_datafile(self,file_path):
        """
        create the original captured frames,encoded in png
        :param file_path: the path of the data pkl file
        """
        f_path=Path(file_path)
        if not f_path.parent.exists():
            f_path.parent.mkdir(parents=True)
        sampler=TestSampler()
        fp=open(file_path,'wb')
        with picamera.PiCamera() as camera:
            rawFrame = PiRGBArray(camera, (640, 480))
            camera.resolution = (640, 480)
            camera.framerate = 15
            shape=(640,480)
            time.sleep(2)
            self.start = time.time()
            cnt=0
            start=time.time()
            prev_cnt=0
            len_sum=0
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                #sample_list, scaled = sampler.sample_and_filter(np.array(frame.array, dtype=np.uint8))
                #self.logger.info('len of sample list is {}'.format(len(sample_list)))
                #len_sum=len_sum+len(sample_list)
                #obj={'img':utils.encode_img(scaled),'shape':shape,'sample':False}
                frame=np.array(frame.array, dtype=np.uint8)
                #frame=utils.imresize_np(frame,1/4,True)
                #pickle.dump(obj,fp,-1)
                pickle.dump(utils.encode_img(frame),fp,-1)
                #for sample in sample_list:
                    #pickle.dump(sample,fp,-1)
                    #self.logger.info('send sample')
                cnt = cnt + 1
                self.count = self.count + 1
                if cnt%10==0:
                    self.logger.info('total sample num is:{}'.format(len_sum))
                    self.logger.info("sent {} frames in {} sec,fps:{}".format(cnt, time.time() - start,
                                                                                 cnt / (time.time() - start)))
                    start=time.time()
                    cnt=0
                    len_sum=0
                if self.count>200:
                    break
                #self.logger.info(cnt)
                rawFrame.seek(0)
                rawFrame.truncate()
                if self.terminate:
                    self.logger.info('terminate')
                    break
        fp.close()
    def create_PSNR_testfile(self,file_path):
        """
        这部分或许可以直接在服务端验证
        :param file_path:
        :return:
        """
        f_path=Path(file_path)
        if not f_path.parent.exists():
            f_path.parent.mkdir(parents=True)
        sampler=TestSampler()
        fp=open(file_path,'wb')
        with picamera.PiCamera() as camera:
            rawFrame = PiRGBArray(camera, (640, 480))
            camera.resolution = (640, 480)
            camera.framerate = 20
            shape=(640,480)
            time.sleep(2)
            self.start = time.time()
            cnt=0
            start=time.time()
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                origin = np.array(frame.array, dtype=np.uint8)
                sample_list, scaled = sampler.sample_and_filter(origin)

                h_n = int(80 * np.ceil(origin.shape[0] / 80))
                w_n = int(80 * np.ceil(origin.shape[1] / 80))
                normed = np.zeros((h_n, w_n, 3), dtype=np.float32) / 255.
                normed[0:origin.shape[0], 0:origin.shape[1], :] = origin

                obj = {'origin': utils.encode_img(normed), 'scaled': utils.encode_img(scaled),'shape':shape}
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
                shape=(img_data.shape[1],img_data.shape[0])
                #img_data=cv2.resize(img_data,(640,480))

                h_n = int(80 * np.ceil(img_data.shape[0] / 80))
                w_n = int(80 * np.ceil(img_data.shape[1] / 80))
                normed = np.zeros((h_n, w_n, 3), dtype=np.float32) / 255.
                normed[0:img_data.shape[0], 0:img_data.shape[1], :] = img_data

                plt.imshow(img_data)
                plt.draw()
                plt.show()
                #print(img_data.shape)
                #print(img_data)
                sample_list, scaled = sampler.sample_and_filter(img_data)
                obj = {'origin': utils.encode_img(img_data), 'scaled': utils.encode_img(scaled),'shape':shape}
                pickle.dump(obj, fp, -1)
                for sample in sample_list:
                    pickle.dump(sample, fp, -1)
                cnt = cnt + 1
                self.logger.info(cnt)
                self.count = self.count + 1
            fp.close()


if __name__ == '__main__':
    pass