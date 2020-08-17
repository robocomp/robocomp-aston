# MPTFeatures(Multi-Person Tracking)
![Tracking Image](project-image-url)


> This component tracks humans and assign them a tracking id. Also provides features based on apperance.  
---
Note: This component is under development


### Table of Contents
- [Description](#description)
- [How To Use](#how-to-use)
- [References](#references)
---

## Description

Multiple human tracking is the process of locating multiple persons over a sequence of frames (video). The MHT problem can be viewed as a data association problem where the goal is to associate detections across frames in a video sequence.

MHT can be divided into 3 steps: 

- **Detection**: In each frame of the video we need to find the bounding box for each person present

- **Multiple Object Tracking**: Multiple Object Tracking is the problem of automatically identifying multiple objects in a video and representing them as a set of trajectories with high accuracy.

- **Person re-identification(ReID)**: Reid is associating images of the same person taken from different cameras or from the same camera at different points in time. Usually, re-identification is constrained to a small time period and a small area covered by cameras 

 
### Technologies
a) **[CenterTrack](https://github.com/xingyizhou/CenterTrack)** 
    presents a simultaneous detection and tracking algorithm that is simple, faste, and accurate. Their tracker, applies a detection model to a pair of images and detections from the prior frame to localizes objects and predicts their associations.

b) **[Torch-reid](https://github.com/KaiyangZhou/deep-person-reid)**
    Torchreid is a library for deep-learning person re-identification, written in PyTorch.    

[Back To The Top](#table-of-contents)

---

## How To Use

#### Requirements
```
pip install -r requirements.txt
```

#### [Installing CenterTrack](!https://github.com/xingyizhou/CenterTrack/blob/master/readme/INSTALL.md)
```
cd $HOME/robocomp-aston/components/detection/HumanIdentification/MPTFeatures/lib/model/networks/
git clone https://github.com/CharlesShang/DCNv2/
cd DCNv2
./make.sh
```


#### [Installing TorchReid](!https://github.com/KaiyangZhou/deep-person-reid#installation)
```
git clone https://github.com/KaiyangZhou/deep-person-reid.git
cd deep-person-reid/
pip install -r requirements.txt
python setup.py develop
```

#### Download Pretrained Weights
download the models and store it here
```
cd $HOME/robocomp-aston/components/detection/HumanIdentification/MPTFeatures/src/PretrainedModels
```
- Centrack trained on COCO dataset: [Official Site](https://drive.google.com/open?id=1tJCEJmdtYIh8VuN8CClGNws3YO7QGd40),  [Copy](https://drive.google.com/file/d/1lbT1AB6HmrsZog9OcehDMPxlwvc1gJdo/view?usp=sharing)


#### Starting each component
For each module open a new terminal(Crtl-Alt-T)  
```
cd $HOME/robocomp-aston/components/detection/HumanIdentification/MPTFeatures
cmake . 
make
cp etc/config etc/config-run
```
*To avoid changing the **config** file in the repository, we can copy it to **config-new** in the component's home directory, so changes will remain untouched by future git pulls.*

After editing the new config file we can run each component
```
python3 src/MPTFeatures.py
```

*By default --gpu = 0. See [opt](./src/lib/opts.py) to see parameters for the module*

---


## References
- CenterTrack 
    > [**Tracking Objects as Points**](http://arxiv.org/abs/2004.01177),            
    > Xingyi Zhou, Vladlen Koltun, Philipp Kr&auml;henb&uuml;hl,        
    > *arXiv technical report ([arXiv 2004.01177](http://arxiv.org/abs/2004.01177))*  


        @article{zhou2020tracking,
        title={Tracking Objects as Points},
        author={Zhou, Xingyi and Koltun, Vladlen and Kr{\"a}henb{\"u}hl, Philipp},
        journal={arXiv:2004.01177},
        year={2020}
        }



- Torchreid
    > [**Tracking Objects as Points**](http://arxiv.org/abs/2004.01177),            
    > Xingyi Zhou, Vladlen Koltun, Philipp Kr&auml;henb&uuml;hl,        
    > *arXiv technical report ([arXiv 2004.01177](http://arxiv.org/abs/2004.01177))*  

        @article{torchreid,
        title={Torchreid: A Library for Deep Learning Person Re-Identification in Pytorch},
        author={Zhou, Kaiyang and Xiang, Tao},
        journal={arXiv preprint arXiv:1910.10093},
        year={2019}
        }

        @inproceedings{zhou2019osnet,
        title={Omni-Scale Feature Learning for Person Re-Identification},
        author={Zhou, Kaiyang and Yang, Yongxin and Cavallaro, Andrea and Xiang, Tao},
        booktitle={ICCV},
        year={2019}
        }

        @article{zhou2019learning,
        title={Learning Generalisable Omni-Scale Representations for Person Re-Identification},
        author={Zhou, Kaiyang and Yang, Yongxin and Cavallaro, Andrea and Xiang, Tao},
        journal={arXiv preprint arXiv:1910.06827},
        year={2019}


[Back To The Top](#table-of-contents)

---

