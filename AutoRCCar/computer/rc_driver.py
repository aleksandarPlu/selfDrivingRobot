import threading
import socketserver
import queue
import collections
import cv2
import numpy as np
import math
import socket
import base64
from imutils.perspective import four_point_transform
from scipy.interpolate import interp1d

sensor_data = " "
test_finish = True
control_queue = queue.Queue(128)
web_queue = queue.Queue(1)
sensor_data_queue = collections.deque(maxlen=3)
sign_active_global = False
manual_control = 1  # 0 - autonomous
                    # 0.5 - semi-autonomous
                    # 1 - manueln


class NeuralNetwork(object):

    def __init__(self):
        self.model = None

    def create(self):
        self.model = cv2.ml.ANN_MLP_load('mlp_xml/mlp.xml')

    def predict(self, samples):
        ret, resp = self.model.predict(samples)
        return resp.argmax(-1)


class RCControl(object):

    def __init__(self):
        pass

    def steer(self, prediction):
        global control_queue
        if prediction == 2:
            control_queue.put('1')
            # print("Forward")
        elif prediction == 0:
            control_queue.put('2')
            # print("Forward-Left")
        elif prediction == 1:
            control_queue.put('8')
            # print("Forward-Right")
        else:
            self.stop()

    def stop(self):
        global control_queue
        control_queue.put('0')


class DistanceToCamera(object):

    def __init__(self):
        # camera params
        self.alpha = 8.0 * math.pi / 180
        self.v0 = 119.865631204
        self.ay = 332.262498472

    def calculate(self, v, h, x_shift, image):
        # compute and return the distance from the target point to the camera
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
        return d


class ObjectDetection(object):

    def __init__(self):
        self.red_light = False
        self.green_light = False
        self.yellow_light = False

    # detecting stop traffic sigh
    def detect(self, cascade_classifier, gray_image, image):

        # y camera coordinate of the target point 'P'
        v = 0
        
        # detection
        cascade_obj = cascade_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # draw a rectangle around the objects
        for (x_pos, y_pos, width, height) in cascade_obj:
            v = y_pos + height - 5

        return v

    # derection for turn left and turn right traffic sign
    def findTrafficSign(self, frame):
        lower_blue = np.array([85, 100, 70])
        upper_blue = np.array([115, 255, 255])

        frameArea = frame.shape[0] * frame.shape[1]

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        largestArea = 0
        largestRect = None

        detectedTrafficSign = None

        if len(cnts) > 0:
            for cnt in cnts:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                sideOne = np.linalg.norm(box[0] - box[1])
                sideTwo = np.linalg.norm(box[0] - box[3])

                area = sideOne * sideTwo

                if area > largestArea:
                    largestArea = area
                    largestRect = box

        v = 0

        if largestArea > frameArea * 0.02:
            v = largestRect[1][1] + (largestRect[0][1] - largestRect[1][1]) - 5
            warped = four_point_transform(mask, [largestRect][0])
            detectedTrafficSign = self.identifyTrafficSign(warped)

        return detectedTrafficSign, v

    def identifyTrafficSign(self, image):

        SIGNS_LOOKUP = {
            (1, 0, 0, 1): 'Turn Right',  # turnRight
            (0, 0, 1, 1): 'Turn Left',  # turnLeft
        }

        THRESHOLD = 150

        image = cv2.bitwise_not(image)
        (subHeight, subWidth) = np.divide(image.shape, 10)
        subHeight = int(subHeight)
        subWidth = int(subWidth)

        leftBlock = image[4 * subHeight:9 * subHeight, subWidth:3 * subWidth]
        centerBlock = image[4 * subHeight:9 * subHeight, 4 * subWidth:6 * subWidth]
        rightBlock = image[4 * subHeight:9 * subHeight, 7 * subWidth:9 * subWidth]
        topBlock = image[2 * subHeight:4 * subHeight, 3 * subWidth:7 * subWidth]

        leftFraction = np.sum(leftBlock) / (leftBlock.shape[0] * leftBlock.shape[1])
        centerFraction = np.sum(centerBlock) / (centerBlock.shape[0] * centerBlock.shape[1])
        rightFraction = np.sum(rightBlock) / (rightBlock.shape[0] * rightBlock.shape[1])
        topFraction = np.sum(topBlock) / (topBlock.shape[0] * topBlock.shape[1])

        segments = (leftFraction, centerFraction, rightFraction, topFraction)
        segments = tuple(1 if segment > THRESHOLD else 0 for segment in segments)

        if segments in SIGNS_LOOKUP:
            return SIGNS_LOOKUP[segments]
        else:
            return None


class SensorDataHandler(socketserver.BaseRequestHandler):

    data = " "

    def handle(self):
        global sensor_data
        global sensor_data_queue
        try:
            while self.data:
                self.data = self.request.recv(1024)
                sensor_data_queue.append(self.data)
        except:
            print("Connection closed on thread 2")


class VideoStreamHandler(socketserver.StreamRequestHandler):

    # h1: stop sign
    h1 = 15.5 - 10  # cm
    # h2: traffic light
    h2 = 15.5 - 10

    # create neural network
    model = NeuralNetwork()
    model.create()

    obj_detection = ObjectDetection()
    rc_car = RCControl()

    # cascade classifiers
    stop_cascade = cv2.CascadeClassifier('cascade_xml/stop_sign.xml')

    d_to_camera = DistanceToCamera()
    d_stop_sign = 60

    stop_start = 0              # start time when stop at the stop sign
    stop_finish = 0
    stop_time = 0
    drive_time_after_stop = 0
    sign_start = 0
    drive_time_after_sign = 0

    sensor_x = [25, 30, 43, 60, 87, 165, 255] # values that we get from IR sensors
    sensor_y = [30, 25, 20, 15, 10, 5, 1] # real distance from car in cm

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.read(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def handle(self):
        global test_finish
        global sensor_data
        global sensor_data_queue
        global sign_active_global
        global web_queue
        stop_flag = False
        stop_sign_active = True
        sign_active = False
        sign_sent = False

        interpolate_sensor = interp1d(self.sensor_x, self.sensor_y, kind='cubic')
        interpolate_sensor.bounds_error = False

        try:
            # stream video frames one by one
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while test_finish:
                length = self.recvall(self.rfile, 16)
                stringData = self.recvall(self.rfile, int(length))
                data = np.fromstring(stringData, dtype='uint8')
                image = cv2.imdecode(data, 1)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                _, t12 = cv2.imencode('.jpg', image)
                b64_img = base64.b64encode(t12)

                sock.sendto(b64_img, ('localhost', 8993))

                # lower half of the image
                half_gray = gray[120:240, :]

                # object detection
                v_param1 = self.obj_detection.detect(self.stop_cascade, gray, image)
                detected_sign, v_param2 = self.obj_detection.findTrafficSign(image)

                if detected_sign is not None and not sign_active:
                    sign_active = True
                    self.sign_start = cv2.getTickCount()

                # distance measurement
                if v_param1 > 0:
                    self.d_stop_sign = self.d_to_camera.calculate(v_param1, self.h1, 300, image)


                # showing video
                # cv2.imshow('image', image)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     pass

                # stop conditions
                sensor_data = []
                try:
                    sensor_data.append(sensor_data_queue.popleft().decode().split(";"))
                    sensor_data.append(sensor_data_queue.popleft().decode().split(";"))
                    sensor_data.append(sensor_data_queue.popleft().decode().split(";"))
                except:
                    pass

                each_sensor_data = [0, 0, 0, 0, 0]
                for data in sensor_data:
                    each_sensor_data[0] += int(data[0])
                    each_sensor_data[1] += int(data[1])
                    each_sensor_data[2] += int(data[2])
                    each_sensor_data[3] += int(data[3])
                    each_sensor_data[4] += int(data[4])

                if sensor_data:
                    each_sensor_data[0] /= len(sensor_data)
                    each_sensor_data[1] /= len(sensor_data)
                    each_sensor_data[2] /= len(sensor_data)
                    each_sensor_data[3] /= len(sensor_data)
                    each_sensor_data[4] /= len(sensor_data)

                tmp_str = ''
                tmp_str += '%.1f' % interpolate_sensor(each_sensor_data[0]) + ';'
                tmp_str += '%.1f' % interpolate_sensor(each_sensor_data[1]) + ';'
                tmp_str += '%.1f' % interpolate_sensor(each_sensor_data[2]) + ';'
                tmp_str += '%.1f' % interpolate_sensor(each_sensor_data[3]) + ';'
                tmp_str += '%.1f' % interpolate_sensor(each_sensor_data[4]) + ';'
                tmp_str += str(detected_sign) + ';'
                tmp_str += str(True if v_param1 > 0 else False) + '\n'

                if web_queue.empty():
                    web_queue.put(tmp_str)

                # for manuel controll we do not need any AI comands
                if manual_control == 1:
                    continue

                # for semi-autonomous we have collision detection and collision avoidance system
                if manual_control == 0.5:
                    if int(each_sensor_data[2]) > 100:
                        self.rc_car.stop()
                        continue
                    continue

                # reshape image
                image_array = half_gray.reshape(1, 38400).astype(np.float32)

                # neural network makes prediction
                prediction = self.model.predict(image_array)

                if int(each_sensor_data[2]) > 100:
                    # print("Stop, obstacle in front")
                    self.rc_car.stop()

                elif 0 < self.d_stop_sign < 55 and stop_sign_active:
                    # print("Stop sign ahead")
                    self.rc_car.stop()

                    # stop for 5 seconds
                    if stop_flag is False:
                        self.stop_start = cv2.getTickCount()
                        stop_flag = True
                    self.stop_finish = cv2.getTickCount()

                    self.stop_time = (self.stop_finish - self.stop_start)/cv2.getTickFrequency()
                    # print("Stop time: %.2fs" % self.stop_time)

                    # 3 seconds later, continue driving
                    if self.stop_time > 3:
                        # print("Waited for 3 seconds")
                        if each_sensor_data[1] > 35 or each_sensor_data[2] > 50:
                            pass
                        else:
                            stop_flag = False
                            stop_sign_active = False

                elif sign_active and not sign_sent:
                    if detected_sign == 'Turn Left':
                        # print('Turn Left sign')
                        control_queue.put('l')
                        sign_sent = True
                    elif detected_sign == 'Turn Right':
                        # print('Turn Right sign')
                        control_queue.put('r')
                        sign_sent = True

                elif int(each_sensor_data[1]) > 90:
                    if int(each_sensor_data[4]) > 70:
                        # print("Stop front-left obstacle")
                        self.rc_car.stop()
                    else:
                        # print("Avoid front-left obstacle")
                        control_queue.put('8')

                elif int(each_sensor_data[3]) > 90:
                    if int(each_sensor_data[0]) > 70:
                        # print("Stop front-right obstacle")
                        self.rc_car.stop()
                    else:
                        # print("Avoid front-right obstacle")
                        control_queue.put('2')

                else:
                    self.rc_car.steer(prediction)
                    self.stop_start = cv2.getTickCount()
                    self.d_stop_sign = 50
                    self.d_sign = 50

                if stop_sign_active is False:
                    self.drive_time_after_stop = (self.stop_start - self.stop_finish)/cv2.getTickFrequency()
                    if self.drive_time_after_stop > 5:
                        stop_sign_active = True

                if sign_active is True:
                    self.drive_time_after_sign = (cv2.getTickCount() - self.sign_start) / cv2.getTickFrequency()
                    if self.drive_time_after_sign > 3:
                        sign_active = False
                        sign_active_global = False
                        sign_sent = False
                        # print("Finish sign detection")

            sock.close()

        except Exception as e:
            print("Connection closed on thread 1")


class ThreadServer(object):

    def __init__(self):
        # sensor - receive data from RPi
        distance_thread = threading.Thread(target=self.server_thread2, args=('localhost', 8002))
        distance_thread.start()
        # video - receive video (jpeg) images from RPi
        video_thread = threading.Thread(target=self.server_thread, args=('localhost', 8000))
        video_thread.start()
        # keyboard i AI controll
        control_thread = threading.Thread(target=self.server_thread3, args=('localhost', 8004))
        control_thread.start()
        # send to web (sensor & sign) - send to client sensor values and detected traffic sign
        web_data_thread = threading.Thread(target=self.server_thread4, args=('localhost', 8992))
        web_data_thread.start()

    def server_thread(self, host, port):
        server = socketserver.TCPServer((host, port), VideoStreamHandler)
        server.serve_forever()

    def server_thread2(self, host, port):
        server = socketserver.TCPServer((host, port), SensorDataHandler)
        server.serve_forever()

    def server_thread3(self, host, port):
        server_socket = socket.socket()
        server_socket.bind((host, port))
        server_socket.listen(0)
        self.server_thread3_rec(server_socket)

    def server_thread3_rec(self, server_socket):
        global control_queue
        global test_finish
        global sign_active_global
        connection, _ = server_socket.accept()

        try:
            while test_finish:

                cmd = control_queue.get(block=True, timeout=None)

                b = bytearray()
                b.extend(map(ord, cmd))
                if not sign_active_global:
                    connection.send(b)
                if cmd == 'l' or cmd == 'r':
                    sign_active_global = True
                control_queue.task_done()
        except ConnectionResetError:
            print("Connection closed on thread 3")
            self.server_thread3_rec(server_socket)
        except ConnectionAbortedError:
            print("Connection closed on thread 3")
            self.server_thread3_rec(server_socket)

    def server_thread4(self, host, port):

        global manual_control
        global control_queue
        lock = threading.Lock()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                s.connect((host, port))
            except:
                continue
            else:
                break
        s.setblocking(True)
        s.settimeout(0.1)

        while test_finish:
            try:
                cmd = web_queue.get(block=True, timeout=None)
                s.send(cmd.encode())
                web_queue.task_done()

                tmp = s.recv(64).decode()
                tmp = tmp[:-2]

                if tmp == 'manual':
                    lock.acquire()
                    manual_control = 1
                    lock.release()
                    control_queue.put('0')
                    # print('manual')
                    continue
                elif tmp == 'auto':
                    lock.acquire()
                    manual_control = 0
                    lock.release()
                    control_queue.put('0')
                    # print('auto')
                    continue
                elif tmp == 'semi':
                    lock.acquire()
                    manual_control = 0.5
                    lock.release()
                    control_queue.put('0')
                    # print('semi')
                    continue

                if manual_control == 1 or manual_control == 0.5:  # jeste mauelno, i onda nase komande stavljaj u queue
                    if tmp != "":
                        control_queue.put(tmp)
            except socket.error as e:
                if e.errno is None:
                    pass
                if e.errno == 10054:
                    print("Connection closed on thread 4")
                    try:
                        self.server_thread4(host, port)
                    except:
                        pass


if __name__ == '__main__':
    ThreadServer()
