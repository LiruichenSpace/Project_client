import threading
import time
import picamera
from picamera.array import PiRGBArray


#直接RGB解码可以获取到RGB格式，但是是（H，W，C）格式的tensor，需要进行调整
class capture_buffer():
    """
    通过start_capture函数来开始，结果存于pool中，可以从中取得
    超过buffer长度的部分会被抛弃
    使用时需要通过pool_lock变量互斥访问
    通过将其变量terminate设为True来停止
    """
    def __init__(self):
        self.pool_lock = threading.Lock()
        self.pool = []
        self.count=0
        self.pool_size=5
        self.terminate=False
        self.start=time.time()
        thread = threading.Thread(target=self.start_capture, args=())  # 不能带括号，直接用函数名调用，否则直接执行了
        thread.setDaemon(True)
        thread.start()#创建对象之后立刻启动
    def start_capture(self):
        with picamera.PiCamera() as camera:
            rawFrame = PiRGBArray(camera,(640,480))
            camera.resolution = (640, 480)
            camera.framerate = 30
            time.sleep(2)
            self.start=time.time()
            for frame in camera.capture_continuous(rawFrame, 'rgb', use_video_port=True):
                with self.pool_lock:
                    while len(self.pool)>self.pool_size:
                        self.pool.pop()
                    self.pool.append(frame.array)
                self.count=self.count+1
                rawFrame.seek(0)
                rawFrame.truncate()
                if self.terminate:
                    print('terminate')
                    break
        print('test')


#capture_pool=capture_buffer()#单例模式，使用时直接从该文件中导入该对象


if __name__ == '__main__':
    buffer=capture_buffer()
    #buffer.start_capture()

    thread=threading.Thread(target=buffer.start_capture,args=())#不能带括号，直接用函数名调用，否则直接执行了
    thread.setDaemon(True)
    thread.start()
    start=time.time()
    while time.time()-buffer.start<10:
        pass
    buffer.terminate=True
    print('Sent %d images in %d seconds at %.2ffps' % (
        buffer.count, time.time() - buffer.start, buffer.count / (time.time() - buffer.start)))