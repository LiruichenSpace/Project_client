# -*- coding:utf8 -*-
import threading
import time

# import cv2
import numpy as np
import picamera
from picamera.array import PiRGBArray


# 直接RGB解码可以获取到RGB格式，但是是（H，W，C）格式的tensor，需要进行调整



class captureBuffer():
    """
    通过start_capture函数来开始，结果存于pool中，可以从中取得
    超过buffer长度的部分会被抛弃
    使用时需要通过pool_lock变量互斥访问
    通过将其变量terminate设为True来停止
    """

    def __init__(self):
        self.pool_lock = threading.Lock()
        self.pool = []
        self.count = 0
        self.pool_size = 5
        self.terminate = False
        self.start = time.time()

    # def start_test(self):
    #     file = open('../test/saved_frames.pkl', 'rb')
    #     try:
    #         while not self.terminate:
    #             image = pickle.load(file)
    #             with self.pool_lock:
    #                 while len(self.pool) >= self.pool_size:
    #                     self.pool.pop()
    #                 self.pool.append(image)
    #     except EOFError:
    #         pass
    #     finally:
    #         file.close()

    def start_capture(self):
        self.pool.clear()
        with picamera.PiCamera() as camera:
            rawFrame = PiRGBArray(camera, (640, 480))
            camera.resolution = (640, 480)
            camera.framerate = 30
            time.sleep(2)
            self.start = time.time()
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                with self.pool_lock:
                    while len(self.pool) > self.pool_size:
                        self.pool.pop()
                    self.pool.append(np.array(frame.array, dtype=np.uint8))
                    self.count = self.count + 1
                rawFrame.seek(0)
                rawFrame.truncate()
                # time.sleep(0.05)
                if self.terminate:
                    print('terminate')
                    break
        print('test')



if __name__ == '__main__':
    # camera=picamera.PiCamera()
    # camera.close()
    buffer = captureBuffer()
    # buffer.start_capture()
    # plt.ion()
    thread = threading.Thread(target=buffer.start_capture, args=())
    # 不能带括号，直接用函数名调用，否则直接执行了
    thread.setDaemon(True)
    thread.start()
    start = time.time()
    while time.time() - buffer.start < 10:
        with buffer.pool_lock:
            if buffer.pool:
                frame = buffer.pool.pop()
                print(frame)
                # plt.imshow(frame)
                # plt.draw()
                # plt.show()
    buffer.terminate = True
    print('Sent %d images in %d seconds at %.2ffps' % (
        buffer.count, time.time() - buffer.start, buffer.count / (time.time() - buffer.start)))
