# LAB2

## Follow these step to start the demo code

##### 1.Check your python version is python3. You can use "python -V" to check.

##### 2.Install pip3.

```
1.sudo apt update

2.sudo apt install python3-pip -y

```

##### 3.Install PyAudio and the requirments pkg.

```
sudo apt-get install portaudio-dev

```
##### after this, check if the path is under  ~/catkin_ws/src/voicegpt, and run 

```
pip3 install -r requirements.txt
```

##### when install are done, unzip voicegpt.zip in catkin_ws/src, direct your path to catkin_ws, and run

```
catkin_make 

source devel/setup.bash

```

##### Remember to key your own api key inside the voicegpt_demo.py, and run

```
rosrun voicegpt_ros voicegpt_demo.py

rosrun voicegpt_ros turtle_control.py
```

##### Now you can try say something to drive turtle
