# MPTFeatures(Multi-Person Tracking)

![MPT Image](../docs/gifs/walk.gif)

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

**Note:- Installation procedure provided [here](../README.md#how-to-use)**  

#### Starting component
For each module open a new terminal(Crtl-Alt-T)  
```
cd $HOME/robocomp-aston/components/detection/HumanIdentification/MPTFeatures
cmake . 
make
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

