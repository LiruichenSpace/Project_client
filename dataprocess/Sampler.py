# -*- coding:utf8 -*-
import numpy as np
import cv2
import utils

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
    def sampling_process(self,data,scaled):
        sample_list = []
        newshape = scaled.shape
        dx, dy = newshape[0] // 6, newshape[1] // 8
        print(dx,dy)
        for i in range(6):
            for j in range(8):
                if np.random.rand() < self.sample_rate:
                    lr = scaled[i * dx:(i + 1) * dx, j * dy:(j + 1) * dy, :]
                    hr = data[i * dx * 4:(i + 1) * dx * 4, j * dy * 4:(j + 1) * dy * 4, :]
                    sample = {'index': (i, j), 'LR': utils.encode_jpeg(lr), 'HR': utils.encode_jpeg(hr)}
                    sample_list.append(sample)
        return sample_list
    def sample_and_filter(self,data):
        """
        执行采样操作，并进行4倍缩放
        :param data: 输入的图像array
        :return
            sample_list: 包含样本的列表
            scaled: 缩放后的图像array
        """
        scaled=cv2.resize(data,dsize=(0,0),fx=0.25,fy=0.25,interpolation=cv2.INTER_NEAREST)
        sample_list=self.sampling_process(data,scaled)
        return sample_list,scaled
