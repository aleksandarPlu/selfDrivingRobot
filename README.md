# selfDrivingRobot

## About

* _**AutoRCCar**_
	* arduino
		* _Code which goes on arduino board_
	* computer
		* cascade_xml <br />
			_xml file generated by haar cascade classifier_
		* mlp_xml <br />
			_xml file neural network_
		* training_xml <br />
			_saved traing data, while on manuel drive_
		* **collect_training_data.py** <br />
			_Code to collect training data while car is under manuel control_
		* **mlp_training.py** <br />
			_Code for training neural network with collected data_
		* **rc_driver.py** <br />
			_Python code for full control of the car_
	* raspberryPi
		* _Pyhon code which goes on RPi_
* _**html**_
	* src/main/java/org/robocode/communication/tmp
		* _Implementation of Java Netty asynchrone TCP server and UDP server for video_
	* src/main/java/org/robocode/config
		* _Configuration java classes for Spring, WebSockets and Java Netty_
	* src/main/java/org/robocode/core
		* _Java classes - entities_
	* src/main/java/org/robocode/rest/controllers
		* _Spring rest controller, rest endpoint_
	* src/main/webapp/app
		* _html pages, javascprint files, css files and pictures for web_
