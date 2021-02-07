# -*- coding:utf8 -*-
import logging

import numpy as np
import cv2
import utils
from queue import PriorityQueue

class BaseSampler():
    def __init__(self):
        self.sample_rate=1.
    def sample_and_filter(self,data):
        pass
class TestSampler(BaseSampler):
    def __init__(self):
        super().__init__()
        #self.data_capturer=data_capturer
        self.sample_rate=0.05
        self.cache0=None
        self.cache1=None
        self.logger=logging.getLogger('base')
    def softsign(self,num):
        return num/(1+num)
    def get_weight(self,img):
        """
        :param img:输入的图像tensor，结构为(H,W,RGB)
        :return: 返回拉普拉斯卷积的结果，目前认为该值可以衡量细节的多少，用于筛选细节较多的样本
        """
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        result = cv2.Laplacian(gray, cv2.CV_64F).var()
        return self.softsign(result)
    def sampling_process_queue(self,data,scaled):
        """
        采用优先级队列实现的版本，测试时有部分样本有很高的权重，但实际上是空白，所以该确定性策略是否合适需要验证
        :param data: 输入的原始图像矩阵，要求格式为（H，W，C）通道最好为RGB
        :param scaled: 缩放（4倍）后的图像矩阵
        :return: 抽样得到的样本列表
        """
        sample_list = PriorityQueue()
        sample_count=int(6*8*self.sample_rate+0.5)
        if self.cache0 is None or self.cache1 is None:#有三个样本即可抽样
            return sample_list
        newshape = scaled.shape
        dx, dy = newshape[0] // 6, newshape[1] // 8
        self.logger.info(dx,dy)
        for i in range(6):
            for j in range(8):
                lr = scaled[i * dx:(i + 1) * dx, j * dy:(j + 1) * dy, :]
                weight=self.get_weight(lr)
                sample={}
                sample_list.put((weight,sample))
                if sample_list.qsize()>sample_count:
                    _,pop_item=sample_list.get()
                else:
                    pop_item=None
                if not (pop_item is None) and not (pop_item is sample):
                    LQs=[]
                    GT=[]
                    tmp=self.cache0[1][i * dx:(i + 1) * dx, j * dy:(j + 1) * dy, :]
                    LQs.append(tmp)
                    LQs.append(lr)
                    tmp=self.cache0[0][i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :]
                    GT.append(tmp)
                    tmp=self.cache1[0][i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :]
                    GT.append(tmp)
                    tmp = data[i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :]
                    GT.append(tmp)
                    sample['LQs']=[utils.encode_jpeg(lr)for lr in LQs]
                    sample['GT']=[utils.encode_jpeg(hr)for hr in GT]
        return [sample for _,sample in list(sample_list)]
    def sampling_process(self,data,scaled):
        """
        采用随机性策略抽取样本，缺少样本数量的确定性，但是可以很大程度加快处理速度，视情况采用
        :param 输入的原始图像矩阵，要求格式为（H，W，C）通道最好为RGB
        :param scaled: 缩放（4倍）后的图像矩阵
        :return: 抽样得到的样本列表
        """
        sample_list = []
        if self.cache0 is None or self.cache1 is None:#有三个样本即可抽样
            return sample_list
        newshape = scaled.shape
        dx, dy = newshape[0] // 6, newshape[1] // 8
        self.logger.info((dx,dy))
        for i in range(6):
            for j in range(8):
                lr = scaled[i * dx:(i + 1) * dx, j * dy:(j + 1) * dy, :]
                if np.random.rand()<self.sample_rate*self.get_weight(lr):
                    LQs=[]
                    GT=[]
                    tmp=self.cache0[1][i * dx:(i + 1) * dx, j * dy:(j + 1) * dy, :]
                    LQs.append(tmp)
                    LQs.append(lr)
                    tmp=self.cache0[0][i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :]
                    GT.append(tmp)
                    tmp=self.cache1[0][i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :]
                    GT.append(tmp)
                    tmp = data[i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :]
                    GT.append(tmp)
                    sample = {'LQs': [utils.encode_jpeg(lr)for lr in LQs], 'GT': [utils.encode_jpeg(hr)for hr in GT]}
                    sample_list.append(sample)
        self.cache0=None
        self.cache1=None #每隔一帧才抽取一次样本
        return sample_list
    def sample_and_filter(self,data):
        """
        执行采样操作，并进行4倍缩放
        :param data: 输入的图像array
        :return
            sample_list: 包含样本的列表
            scaled: 缩放后的图像array
        """
        scaled=cv2.resize(data,dsize=(0,0),fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)# 目前的AREA方法可以获得类似的效果，需要验证此缩放策略的结果如何
        #print(data)
        #scaled=utils.imresize_np(data,0.25,True)/255.
        print(scaled.shape)
        sample_list=self.sampling_process(data,scaled)
        self.cache0 = self.cache1
        self.cache1 = (data,scaled)
        return sample_list,scaled
