# -*- coding:utf8 -*-
import dataCapture
import numpy as np

class BaseSampler():
    def __init__(self):
        self.sample_rate=1.
    def sample_and_filter(self,data):
        pass
class TestSampler(BaseSampler):
    def __init__(self,data_capturer:dataCapture.captureBuffer):
        super.__init__()
        self.data_capturer=data_capturer
        self.sample_rate=0.1
    def sampling_process(self):
        pass
    def sample_and_filter(self,data):
        sample_list=[]
        for i in range(6):
            for j in range(8):
                if np.random.rand()<self.sample_rate:
                    pass
        return sample_list
