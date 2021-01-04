import io
import time

#import cv2
import numpy as np
import picamera
from PIL import Image


def start_camera():
    camera=picamera.PiCamera()
    camera.start_preview()
    time.sleep(2)
    return camera

def stop_camera(camera):
    camera.stop_preview()


def get_pic_stream(camera):
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg')
    # 将指针指向流的开始

    return stream

def get_pil_object(camera):
    stream=get_pic_stream(camera)
    stream.seek(0)
    return Image.open(stream)

# def get_cv_object(camera):
#     stream = get_pic_stream(camera)
#     # 从流构建numpy
#     data = np.fromstring(stream.getvalue(), dtype=np.uint8)
#     # 通过opencv解码numpy
#     image = cv2.imdecode(data, 1)
#     # opencv解码后返回以RGB解码的图像数据,不进行此操作，返回BGR格式
#     #image = image[:, :, ::-1]
#     return image