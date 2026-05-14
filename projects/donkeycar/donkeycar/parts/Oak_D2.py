import cv2
import depthai as dai
import time
import threading

# class oakD2:
#     def __init__(self, image_w=224, image_h= 224, image_d=3, framerate=30, **kwargs):
#         # Connect to device and start pipeline
#         with dai.Device() as device:
#             self.device = device
#             # Device name
#             print('Device name:', device.getDeviceName())
#             # Bootloader version
#             if device.getBootloaderVersion() is not None:
#                 print('Bootloader version:', device.getBootloaderVersion())
#             # Print out usb speed
#             print('Usb speed:', device.getUsbSpeed().name)
#             # Connected cameras
#             print('Connected cameras:', device.getConnectedCameraFeatures())

#             # Create pipeline
#             self.pipeline = dai.Pipeline()
#             self.cams = device.getConnectedCameraFeatures()
#             self.streams = []
#             for cam in self.cams:
#                 print(str(cam), str(cam.socket), cam.socket)
#                 c = self.pipeline.create(dai.node.Camera)
#                 x = self.pipeline.create(dai.node.XLinkOut)
#                 c.isp.link(x.input)
#                 c.setBoardSocket(cam.socket)
#                 stream = str(cam.socket)
#                 if cam.name:
#                     stream = f'{cam.name} ({stream})'
#                 x.setStreamName(stream)
#                 self.streams.append(stream)
#             self.device.startPipeline(self.pipeline)
#             self.lock = threading.Lock()
#             self.on = True
#             self.frame = None
        
#     def update(self):
#         while self.on:
#             queueNames = self.device.getQueueEvents(self.streams)
#             for stream in queueNames:
                
#                 messages = self.device.getOutputQueue(stream).tryGetAll()
#                 for message in messages:
#                     # Display arrived frames
#                     if type(message) == dai.ImgFrame:
#                         self.frame = message.getCvFrame()


#     def run_threaded(self):
#         return self.frame
    
#     def run(self):
#         return self.run_threaded(self)
    
#     def shutdown(self):
#         self.on = False
#         self.device.close()

class oakD2:
    def __init__(self, image_w=224, image_h=224, image_d=3, framerate=30, **kwargs):
        # Create device without context manager so it stays alive
        self.device = dai.Device()

        print('Device name:', self.device.getDeviceName())
        if self.device.getBootloaderVersion() is not None:
            print('Bootloader version:', self.device.getBootloaderVersion())
        print('Usb speed:', self.device.getUsbSpeed().name)
        print('Connected cameras:', self.device.getConnectedCameraFeatures())

        self.pipeline = dai.Pipeline()
        self.cams = self.device.getConnectedCameraFeatures()
        self.streams = []

        for cam in self.cams:
            print(str(cam), str(cam.socket), cam.socket)
            c = self.pipeline.create(dai.node.Camera)
            x = self.pipeline.create(dai.node.XLinkOut)
            c.isp.link(x.input)
            c.setBoardSocket(cam.socket)

            # Use a simple, space-free stream name to avoid queue lookup issues
            stream = cam.socket.name  # e.g. 'CAM_A', 'CAM_B'
            if cam.name:
                stream = f'{cam.name}_{cam.socket.name}'  # e.g. 'color_CAM_A'
            x.setStreamName(stream)
            self.streams.append(stream)

        self.device.startPipeline(self.pipeline)

        self.lock = threading.Lock()
        self.on = True
        self.frame = None

    def update(self):
        while self.on:
            queueNames = self.device.getQueueEvents(self.streams)
            for stream in queueNames:
                messages = self.device.getOutputQueue(stream).tryGetAll()
                for message in messages:
                    if isinstance(message, dai.ImgFrame):
                        with self.lock:
                            self.frame = message.getCvFrame()

    def run_threaded(self):
        with self.lock:
            return self.frame

    def run(self):
        return self.run_threaded()  # Fixed: was incorrectly passing self as argument

    def shutdown(self):
        self.on = False
        self.device.close()