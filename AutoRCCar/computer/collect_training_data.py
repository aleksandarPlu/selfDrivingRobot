import numpy as np
import cv2
import serial
import pygame
from pygame.locals import *
import socket
import time
import os


class CollectTrainingData(object):
    
    def __init__(self):

        # connect to socket for receiving camera from RPi
        self.server_socket_camera = socket.socket()
        self.server_socket_camera.bind(('localhost', 8000))
        self.server_socket_camera.listen(0)

        # accept a single connection
        self.connection_camera = self.server_socket_camera.accept()[0].makefile('rb')

        # connect to socket for sending conntrols to arduino via RPi
        self.server_socket_control = socket.socket()
        self.server_socket_control.bind(('localhost', 8004))
        self.server_socket_control.listen(0)
        self.connection_control, _ = self.server_socket_control.accept()

        self.send_inst = True

        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1
        self.temp_label = np.zeros((1, 4), 'float')

        pygame.init()
        pygame.display.set_mode((320, 240))
        self.collect_image()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.read(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def collect_image(self):

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print('Start collecting images...')
        e1 = cv2.getTickCount()
        image_array = np.zeros((1, 38400))
        label_array = np.zeros((1, 4), 'float')

        # stream video frames one by one
        try:
            frame = 1
            while self.send_inst:
                length = self.recvall(self.connection_camera, 16)
                stringData = self.recvall(self.connection_camera, int(length))
                data = np.fromstring(stringData, dtype='uint8')
                tmp_image = cv2.imdecode(data, 1)
                image = cv2.cvtColor(tmp_image, cv2.COLOR_BGR2GRAY)

                # select lower half of the image
                roi = image[120:240, :]

                # save streamed images
                cv2.imshow('roi_image', roi)
                cv2.imshow('image', tmp_image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    pass

                # reshape the roi image into one row array
                temp_array = roi.reshape(1, 38400).astype(np.float32)

                frame += 1
                total_frame += 1

                # get input from human driver
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        key_input = pygame.key.get_pressed()

                        # complex orders
                        if key_input[pygame.K_UP] and key_input[pygame.K_RIGHT]:
                            print("Forward Right")
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[1]))
                            saved_frame += 1
                            b = bytearray()
                            b.extend(map(ord, '8'))
                            self.connection_control.send(b)

                        elif key_input[pygame.K_UP] and key_input[pygame.K_LEFT]:
                            print("Forward Left")
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[0]))
                            saved_frame += 1
                            b = bytearray()
                            b.extend(map(ord, '2'))
                            self.connection_control.send(b)

                        elif key_input[pygame.K_DOWN] and key_input[pygame.K_RIGHT]:
                            print("Reverse Right")
                            b = bytearray()
                            b.extend(map(ord, '6'))
                            self.connection_control.send(b)

                        elif key_input[pygame.K_DOWN] and key_input[pygame.K_LEFT]:
                            print("Reverse Left")
                            b = bytearray()
                            b.extend(map(ord, '4'))
                            self.connection_control.send(b)

                        # simple orders
                        elif key_input[pygame.K_UP]:
                            print("Forward")
                            saved_frame += 1
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[2]))
                            b = bytearray()
                            b.extend(map(ord, '1'))
                            self.connection_control.send(b)

                        elif key_input[pygame.K_DOWN]:
                            print("Reverse")
                            saved_frame += 1
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[3]))
                            b = bytearray()
                            b.extend(map(ord, '5'))
                            self.connection_control.send(b)

                        elif key_input[pygame.K_RIGHT]:
                            print("Right")
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[1]))
                            saved_frame += 1
                            b = bytearray()
                            b.extend(map(ord, '7'))
                            self.connection_control.send(b)

                        elif key_input[pygame.K_LEFT]:
                            print("Left")
                            image_array = np.vstack((image_array, temp_array))
                            label_array = np.vstack((label_array, self.k[0]))
                            saved_frame += 1
                            b = bytearray()
                            b.extend(map(ord, '3'))
                            self.connection_control.send(b)

                        elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                            print('exit')
                            self.send_inst = False
                            b = bytearray()
                            b.extend(map(ord, '0'))
                            self.connection_control.send(b)
                            break

                    elif event.type == pygame.KEYUP:
                        b = bytearray()
                        b.extend(map(ord, '0'))
                        self.connection_control.send(b)

            train = image_array[1:, :]
            train_labels = label_array[1:, :]

            # save training data as a numpy file
            file_name = str(int(time.time()))
            directory = "training_data"
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:    
                np.savez(directory + '/' + file_name + '.npz', train=train, train_labels=train_labels)
            except IOError as e:
                print(e)

            e2 = cv2.getTickCount()
            # calculate streaming duration
            time0 = (e2 - e1) / cv2.getTickFrequency()
            print('Streaming duration:', time0)

            print(train.shape)
            print(train_labels.shape)
            print('Total frame:', total_frame)
            print('Saved frame:', saved_frame)
            print('Dropped frame', total_frame - saved_frame)

        finally:
            self.connection_camera.close()
            self.connection_control.close()
            self.server_socket_camera.close()
            self.server_socket_control.close()

if __name__ == '__main__':
    CollectTrainingData()
