# faceFeatures (Face Recognition Component)
![Face Recognition Image Image](../docs/images/face_recognition.png)



> This component detects multiple human face and provides features for face recognition.   
---
Note: This component is under development


### Table of Contents
- [Description](#description)
- [How To Use](#how-to-use)
- [References](#references)
---

## Description

Facial recognition is used to automatically label an individualin by retrieving it's face features. 

It can be divided into 2 steps: 

- **Detection**: In each frame of the video we need to find the bounding box for each person's face. To choose the technique to integrate, we compare their performance and computation time. 

    ![Face Detection performance](../docs/images/facedetection_performance.png)

    ![Face Detection time](../docs/images/facedetection_time.png)


    Based on these results, I have integrated mt-cnn as the face-detection model. 

- **Recognition**: Face recognition is a method of identifying or verifying the identity of an individual using their face.

    Top performers: 

    1. [ArcFace](!https://arxiv.org/pdf/1801.07698.pdf)
    ```
    Below I discuss 2 versions of ArcFace. 
    1. Using Resnet-100 as the backbone
    2. Using MobileFacenet as the backbone 
    ```
    2. [CosFace](!)  
    3. Face-net (Currently used by Robocomp)  

        ![Face Recognition performance](../docs/images/performance_face.png)

        ![Face Recognition time](../docs/images/time_face.png)

    ```
      Based on these results, I have integrated Arcface as the face-recognition model. 
    ```
 
[Back To The Top](#table-of-contents)

---

## How To Use

#### Requirements
```
pip install -r requirements.txt
```
#### Download Pretrained Weights
download the models, unzip the folder and store it here
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



#### Starting component
For each module open a new terminal(Crtl-Alt-T)  
```
cd $HOME/robocomp-aston/components/detection/HumanIdentification/faceFeatures
cmake . 
make
cp etc/config etc/config-run
```
*To avoid changing the **config** file in the repository, we can copy it to **config-new** in the component's home directory, so changes will remain untouched by future git pulls.*

After editing the new config file we can run each component
```
python3 src/faceFeatures.py 
```

*By default --model = "./src/PretrainedModels/model-y1-test2 & --gpu = 0. See [opt](./src/faceFeatures.py) to see parameters for the module*

---


## References

> [**Mtcnn detection + arc face**](https://github.com/Yoonhee-Gil/mtcnn-arcface),            
> Yoonhee Gil-2019

```
@inproceedings{deng2019retinaface,
title={RetinaFace: Single-stage Dense Face Localisation in the Wild},
author={Deng, Jiankang and Guo, Jia and Yuxiang, Zhou and Jinke Yu and Irene Kotsia and Zafeiriou, Stefanos},
booktitle={arxiv},
year={2019}
}

@inproceedings{guo2018stacked,
  title={Stacked Dense U-Nets with Dual Transformers for Robust Face Alignment},
  author={Guo, Jia and Deng, Jiankang and Xue, Niannan and Zafeiriou, Stefanos},
  booktitle={BMVC},
  year={2018}
}

@article{deng2018menpo,
  title={The Menpo benchmark for multi-pose 2D and 3D facial landmark localisation and tracking},
  author={Deng, Jiankang and Roussos, Anastasios and Chrysos, Grigorios and Ververas, Evangelos and Kotsia, Irene and Shen, Jie and Zafeiriou, Stefanos},
  journal={IJCV},
  year={2018}
}

@inproceedings{deng2018arcface,
title={ArcFace: Additive Angular Margin Loss for Deep Face Recognition},
author={Deng, Jiankang and Guo, Jia and Niannan, Xue and Zafeiriou, Stefanos},
booktitle={CVPR},
year={2019}
}
```

[Back To The Top](#table-of-contents)

---