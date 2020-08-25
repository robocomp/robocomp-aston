# Human re-identification using multi-modal perception system

<iframe width="560" height="315" src="https://www.youtube.com/embed/Lt7oiOuUIJA" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

> This component uses modalities such as face-recognition,gait-recognition, multi-person tracking for human identification.
---
Note: This component is under development


### Table of Contents
- [Description](#description)
- [System Design](#system-design)
- [How To Use](#how-to-use)
- [License](#license)
- [Author Info](#author-info)
---

## Description

In Robotics, it is crucial to identify humans and efficiently distinguish them. This gives the ability to perform further challenging tasks such as personalized interactions, social navigation and surveillance. The aim of this project is to integrate different aspects such as face, silhouette and apperance of the body. Using different human identification methods (such as gait recognition & person re-identification) these features will be extracted. Finally a multi-modal pipeline is used to integrate these components into Robocomp.


![Pipeline](./docs/images/MainPipeline.png)

**Fig-1. Pipeline for human identification. (a) Detect humans and assign them a tracking id. (b) Segment human and extract gait features (c) Detect face and extract features (d) Combine features & search identity from the database.**


### Technologies
As shown in figure-1, 3 seperate techniques capture different modalites of the input video.

a) **[Multi-Person Tracking Component](./MPTFeatures/README.md)** 
    
This component detects persons at every rgb frames. Then it associates them with humans detected in previous frames. Thus, it tracks humans present and assign them a tracking id(eg. XXXXX). This is also essential for short-term human identification. 

b) **[Gait Recognition Component](./gaitFeatures/README.md)** 

Gait analysis is a soft biometric for long-term human identification. The segmentation mask for every human is extracted and stored across several frames. Based on the walking pattern, a deep learning model extractes features for recognition.  

c) **[Face Recognition Component](./faceFeatures/README.md)** 

Face recognition is the most widely used method for human-identication. First step is to detect the face followed by extracting features using a deep learning model.

d) **[Multi Modal Human Identification Component](./multiModalHumanIdentification/README.md)**

This component will make a call to different components, combine their features and search the database/gallery to identify the person. If no person is identified, the data is added to the gallery as an *unknown person*.  


[Back To The Top](#table-of-contents)

---

## System Design

![Robocomp Component Design](./docs/images/RobocompComponentDesign.png)

**Fig-2. System diagram for communication between robocomp components. Given input video from <span style="color:green"> CameraSimple</span>, first track persons in the video using <span style="color:red"> MPTFeatures</span>. For each person get the face features and gait features using <span style="color:red">faceFeatures & gaitFeatures</span> respectively. Next <span style="color:red">multiModalHumanIdentification</span> will fuse the features and search the <span style="color:grey">database</span>. Finally the label and the boudning boxes and returned to the <span style="color:green"> humanIdentificationClient</span>  module**

## How To Use

#### Installing robocomp
Use the steps provided at this link: https://github.com/robocomp/robocomp#installation-itself 

#### Requirements
```
pip install -r requirements.txt
```

#### Installing modules

#### [MPTFeatures](./MPTFeatures/README.md#how-to-use)


- [Installing CenterTrack](https://github.com/xingyizhou/CenterTrack/blob/master/readme/INSTALL.md)
    ```
    cd $HOME/robocomp-aston/components/detection/HumanIdentification/MPTFeatures/src/lib/model/networks/
    git clone https://github.com/CharlesShang/DCNv2/
    cd DCNv2
    sudo python3 setup.py build develop
    ```

    Note:- If you are facing issues installing look [here](https://github.com/xingyizhou/CenterTrack/issues)

- [Installing TorchReid](https://github.com/KaiyangZhou/deep-person-reid#installation)
    ```
    git clone https://github.com/KaiyangZhou/deep-person-reid.git
    cd deep-person-reid/
    pip install -r requirements.txt
    sudo python3 setup.py develop
    ```

- Download Pretrained Weights & store them here:
    ```
    cd $HOME/robocomp-aston/components/detection/HumanIdentification/MPTFeatures/src/PretrainedModels
    ```

    Link to weights: 
    - Centrack trained on COCO dataset: [Official Site](https://drive.google.com/open?id=1tJCEJmdtYIh8VuN8CClGNws3YO7QGd40),  [Copy](https://drive.google.com/file/d/1lbT1AB6HmrsZog9OcehDMPxlwvc1gJdo/view?usp=sharing)

    After downloading the directory should look like this:
    ```
    MPTFeatures/src/PretrainedModels
    └── coco_tracking.pth
    ```

#### [faceFeatures](./faceFeatures/README.md#how-to-use)

- Download Pretrained Weights, unzip the folder and store it here
    ```
    cd $HOME/robocomp-aston/components/detection/HumanIdentification/faceFeatures/src/PretrainedModels
    ```

    Link to weights: 
    - Mt-cnn: [Link](https://drive.google.com/drive/folders/1vvoMe4tSzI59GjtRLtDJu8vkX4jxR06P?usp=sharing)
    - ArFace-MobileNet: [Link1](https://www.dropbox.com/s/akxeqp99jvsd6z7/model-MobileFaceNet-arcface-ms1m-refine-v1.zip?dl=0), [Link2](https://drive.google.com/drive/folders/1gdwQBSMr7dLyLUWoBAKw2IfBUJqZFNHv?usp=sharing)
    - ArcFace-Resnet100: [Link](https://www.dropbox.com/s/tj96fsm6t6rq8ye/model-r100-arcface-ms1m-refine-v2.zip?dl=0)

    After downloading the directory should look like this:
    ```
    src/PretrainedModels
    ├── model-r100-ii
    │   ├── log
    │   ├── model-0000.params
    │   └── model-symbol.json
    ├── model-y1-test2
    │   ├── log
    │   ├── model-0000.params
    │   └── model-symbol.json
    └── mtcnn-model
        ├── det1-0001.params
        ├── det1.caffemodel
        ├── det1.prototxt
        ├── det1-symbol.json
        ├── det2-0001.params
        ├── det2.caffemodel
        ├── det2.prototxt
        ├── det2-symbol.json
        ├── det3-0001.params
        ├── det3.caffemodel
        ├── det3.prototxt
        ├── det3-symbol.json
        ├── det4-0001.params
        ├── det4.caffemodel
        ├── det4.prototxt
        └── det4-symbol.json
    ```


#### [gaitFeatures](./gaitFeatures/README.md#how-to-use)

- Download Pretrained Weights & store them here:
    ```
    cd $HOME/robocomp-aston/components/detection/HumanIdentification/gaitFeatures/src/PretrainedModels
    ```
    Links to wieights: 
    - GaitSet: [Official](https://github.com/AbnerHqC/GaitSet/blob/master/work/checkpoint/GaitSet/GaitSet_CASIA-B_73_False_256_0.2_128_full_30-80000-encoder.ptm), [Copy](https://drive.google.com/file/d/1SUOPjFBoci4MuXwUgG5arvVzeAw-t7j7/view?usp=sharing)
    - Human Segmentation(UNet): [Official](https://drive.google.com/file/d/14QxasSCcL_ij7NHR7Fshx5fi5Sc9MleD/view?usp=sharing), [Copy](https://drive.google.com/file/d/14QxasSCcL_ij7NHR7Fshx5fi5Sc9MleD/view?usp=sharing)

    After downloading the directory should look like this:
    ```
    src/PretrainedModels
    ├── GaitSet_CASIA-B_73_False_256_0.2_128_full_30-80000-encoder.ptm
    └── UNet_ResNet18.pth
    ```


#### Running with default setting 
You can run all components in default setting run:
```
# To use CameraSimple
./run.sh

# To run on webcam
./run.sh webcam

# To run on video 
./run.sh <video-path>
```

#### Or manually starting each component
For each module open a new terminal(Crtl-Alt-T)  
```
cd $HOME/robocomp-aston/components/detection/HumanIdentification/<Component_DIR>/
cmake . 
make
```
*To avoid changing the **config** file in the repository, we can copy it to **config-new** in the component's home directory, so changes will remain untouched by future git pulls.*

Configuration parameters

You must ensure the proxies, hostname and port number of 
```
    FaceFeatures/etc/config, 
    MPTFeatures/etc/config,
    GaitFeatures/etc/config,
    multiModalHumanIdentification/etc/config,
    test/humanIdentificationClient/etc/config, 
    ../../hardware/camera/camerasimple/etc/config,
```

match the endpoints in the config files of the corresponding interfaces.


#### Testing
After editing the new config file we can run each component
```
cd $ROOT_DIR/robocomp-aston/components/detection/HumanIdentification/<Component_DIR>
python3 src/<component_name>.py --parameter parameter_value 
```




#### Adding person to database 
<img src="./docs/gifs/database_add.gif" width="960" height="480"/>

**Fig-3 Run the client application, double-click on the person thats needed to be added. Type the name. Click OK.**

#### Deleting person from database

<img src="./docs/gifs/database_delete.gif" width="960" height="480"/>

**Fig-4 Run the client application, double-click on the person thats needed to be deleted**

[Back To The Top](#table-of-contents)

---


## License
Copyright (C) [2020] by RoboComp

RoboComp is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RoboComp is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.


[Back To The Top](#table-of-contents)

---

## Author Info

- RoboComp          - https://robocomp.github.io/web/
- Shubh Maheshwari  - https://github.com/shubhMaheshwari

[Back To The Top](#table-of-contents)
