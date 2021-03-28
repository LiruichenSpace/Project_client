# -*- coding:utf8 -*-
import logging

import numpy as np
import cv2
import utils
from queue import PriorityQueue
import queue
class BaseSampler():
    def __init__(self):
        self.sample_rate=1.
    def sample_and_filter(self,data):
        pass
class TestSampler(BaseSampler):
    def __init__(self,upper_rate=0.1,lower_rate=0,sample_len=3):#设定最高和最低学习采样率
        super().__init__()
        #self.data_capturer=data_capturer
        self.sample_rate=0.03
        self.upper_rate=upper_rate
        self.lower_rate=lower_rate
        self.cache0=None
        self.cache1=None
        self.cache=[]
        self.sample_len=sample_len
        self.logger=logging.getLogger('base')
    def softsign(self,num):
        return num/(1+num)
    def get_weight(self,img):
        """
        :param img:输入的图像tensor，结构为(H,W,RGB)
        :return: 返回拉普拉斯卷积的结果，目前认为该值可以衡量细节的多少，用于筛选细节较多的样本
        """
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        result = cv2.Laplacian(gray, cv2.CV_32F).var()
        #result = cv2.Laplacian(gray, -1).var()
        #self.logger.info(result)
        #return self.softsign(result)
        return result
    def sampling_process(self,data,scaled,shape):
        """
        采用随机性策略抽取样本，缺少样本数量的确定性，但是可以很大程度加快处理速度，视情况采用
        :param 输入的原始图像矩阵，要求格式为（H，W，C）通道最好为RGB
        :param scaled: 缩放（4倍）后的图像矩阵
        :return: 抽样得到的样本列表
        """
        sample_list = []
        #if self.cache0 is None or self.cache1 is None:
            #return sample_list
        dx=dy=20
        self.cache.append((data,scaled,shape))
        for i in range(shape[0]//dy):
            for j in range(shape[1]//dx):
                #lr = scaled[i * dx:(i + 1) * dx, j * dy:(j + 1) * dy, :]
                if np.random.rand()<self.sample_rate:#*self.get_weight(lr):
                    LQs = []
                    GT = []
                    #self.logger.info('cache len is {}'.format(len(self.cache)))
                    for index in range(len(self.cache)):
                        GT.append(self.cache[index][0][i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :])
                        if index%2==0:
                            LQs.append(self.cache[index][1][i * dx:(i + 1) * dx, j * dy:(j + 1) * dy, :])
                    sample = {'LQs': [utils.encode_img(lr) for lr in LQs], 'GT': [utils.encode_img(hr) for hr in GT]
                        ,'sample':True}
                    sample_list.append(sample)
        self.cache.clear()
        self.cache.append((data,scaled,shape))
        #chean sample cache
        return sample_list
    def sample_and_filter(self,data):
        """
        执行采样操作，并进行4倍缩放
        :param data: 输入的图像array
        :return
            sample_list: 包含样本的列表
            scaled: 缩放后的图像array
        """
        h_n = int(16 * np.ceil(data.shape[0] / 16))#TODO: duplicate here
        w_n = int(16 * np.ceil(data.shape[1] / 16))
        #print(data.shape)
        normed=np.zeros((h_n,w_n,3),dtype=np.float32)
        #print(normed.shape)
        normed[0:data.shape[0],0:data.shape[1],:]=data
        scaled=cv2.resize(normed,dsize=(0,0),fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA)# 目前的AREA方法可以获得类似的效果，需要验证此缩放策略的结果如何
        #此处无法直接使用，故采用AREA策略
        #scaled=utils.imresize_np(normed,1/4,True)
        #print(scaled.shape)
        sample_list=[]
        if len(self.cache)==self.sample_len-1:
            sample_list=self.sampling_process(normed,scaled,(data.shape[0]//4,data.shape[1]//4))
        self.cache.append((normed,scaled,(data.shape[0]//4,data.shape[1]//4)))
        data=None
        return sample_list,scaled