import os
import pickle

import cv2
import matplotlib.pyplot as plt
import numpy as np

import utils
from dataprocess.Sampler import TestSampler
#from dataprocess.dataCapture import captureBuffer

def create_dataset_testfile(dir_path, out_path):
    subdir_list = os.listdir(dir_path)
    sampler = TestSampler()
    plt.ion()
    plt.figure(1)
    for name in subdir_list:
        print('start process {}:'.format(name))
        cnt = 0
        fp = open(os.path.join(out_path, str(name) + '.pkl'), 'wb')
        img_namelist = os.listdir(os.path.join(dir_path, name))
        img_namelist = np.sort(img_namelist)
        for img in img_namelist:
            img_path = os.path.join(dir_path, name, img)
            img_data = cv2.imread(img_path, cv2.IMREAD_COLOR)
            img_data = cv2.resize(img_data, (640, 480))
            #img_data=np.copy(img_data[:,:,::-1])

            # print(img_data.shape)
            # print(img_data)
            sample_list, scaled = sampler.sample_and_filter(img_data)
            plt.imshow(scaled[:,:,::-1])
            plt.draw()
            plt.show()
            obj = {'origin': utils.encode_img(img_data), 'scaled': utils.encode_img(scaled)}
            pickle.dump(obj, fp, -1)
            for sample in sample_list:
                pickle.dump(sample, fp, -1)
            cnt = cnt + 1
            print(cnt)
        fp.close()

if __name__ == '__main__':
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    create_dataset_testfile('D:\Datasets\Vid4\HR','D:\Datasets\Vid4\Vid4_jpg')