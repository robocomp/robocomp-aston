# FacialEmotionRecognition

Note: This component is under development. Currently it can generate a bounding box across the facial images and display the facial emotion.

## Resolving dependencies

face_recognition

## Configuration parameters
As an example, `FacialEmotionRecognition` component parameters are characterized in config file described below:

```
# Endpoints for implements interfaces
FacialEmotionRecognition.Endpoints=tcp -p 10015

# Proxies for required interfaces
CameraSimpleProxy = camerasimple:tcp -h localhost -p 10005

Ice.Warn.Connections=0
Ice.Trace.Network=0
Ice.Trace.Protocol=0

```

You must ensure the proxies, hostname and port number of `CameraSimpleProxy` and `FacialEmotionRecognition` match the endpoints in the config files of the corresponding interfaces.
    
## Starting the component
To avoid changing the *config* file in the repository, we can copy it to the component's home directory, so changes will remain untouched by future git pulls.

Download the trained model from this [link](https://drive.google.com/file/d/1aygo0currK-E12DFzlOZ3iSXxq0YUUMJ/view?usp=sharing), move it in the `FacialEmotionRecognition/model` directory and unzip it. Once the model is in the correct directory open one more terminal and follow these instructions.

Terminal 1:
```
cd hardware/camera/camerasimple
python src/camerasimple.py etc/config-run
```

Terminal 2:
```
cd detection/FacialEmotionRecognition
python src/FacialEmotionRecognition.py etc/config-run
```

Once the component is running, user can see the camera feed with bounding box across the faces in a pop-up window. The Facial Images, output of the softmax layer of the model and the bounding box coordinates of the faces are also returned by the function `getEmotionList()` implemented in the component.