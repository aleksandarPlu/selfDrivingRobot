from socket import *
import time
import serial
import threading
import cv2
import numpy as np


ser = serial.Serial('COM4', 9600, timeout=0)
camera_socket = socket(AF_INET, SOCK_STREAM)
sensor_socket = socket(AF_INET, SOCK_STREAM)
control_socket = socket(AF_INET, SOCK_STREAM)


# create a socket and bind socket to the host
def connect():
    try:
        camera_socket.connect(('192.168.1.2', 8000))
        sensor_socket.connect(('192.168.1.2', 8002))
        control_socket.connect(('192.168.1.2', 8004))
    except:
        connect()


connect()


def receive_distance_data():
    try:
        data = ser.readline()
        tmp = len(data)
        if not len(data.decode().split(';')) == 6:
            data = ''
    except ser.SerialTimeoutException:
        print('Data could not be read')
        time.sleep(1)

    return data.strip()


def handle_camera(cap1):
    ret1, frame1 = cap1.read()
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode('.jpg', frame1, encode_param)
    data = np.array(imgencode)
    string_data = data.tostring()
    b = bytearray()
    b.extend(map(ord, str(len(string_data)).ljust(16)))
    camera_socket.send(b)
    camera_socket.send(string_data)


class ThreadServer(object):

    def __init__(self):
        distance_thread = threading.Thread(target=self.server_thread2)
        distance_thread.start()
        video_thread = threading.Thread(target=self.server_thread)
        video_thread.start()

    def server_thread(self):
        global camera_socket
        cap1 = cv2.VideoCapture(0)

        cap1.set(3, 320)
        cap1.set(4, 240)
        cap1.set(6, 10)

        time.sleep(2)

        while True:
            try:
                handle_camera(cap1)
            except:
                try:
                    camera_socket = socket(AF_INET, SOCK_STREAM)
                    camera_socket.connect(('192.168.1.2', 8000))
                except OSError:
                    camera_socket.close()

        cap.release()

    def server_thread2(self):
        global sensor_socket
        while True:
            distance = receive_distance_data()
            if distance:
                try:
                    sensor_socket.send(distance)
                except:
                    try:
                        sensor_socket = socket(AF_INET, SOCK_STREAM)
                        sensor_socket.connect(('192.168.1.2', 8002))
                    except OSError:
                        sensor_socket.close()

            time.sleep(0.01)

try:
    ThreadServer()
    control_socket.setblocking(False)
    while True:
        try:
            msg = control_socket.recv(1024)
            # print(msg)
            ser.write(msg)
        except:
            try:
                control_socket = socket(AF_INET, SOCK_STREAM)
                control_socket.connect(('192.168.1.2', 8004))
            except OSError:
                control_socket.close()

finally:
    control_socket.close()
    camera_socket.close()
    sensor_socket.close()
    ser.close()
