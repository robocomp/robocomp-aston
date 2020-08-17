#!/bin/bash 

# # Run face features
gnome-terminal --disable-factory -- /bin/bash -c --disable-factory 'cd $PWD/faceFeatures; cmake . ; make ; python3 src/faceFeatures.py' &

# # Run Reid Features for tracking humans
gnome-terminal --disable-factory -- /bin/bash -c 'cd $PWD/MPTFeatures ;cmake . ; make ; python3 src/MPTFeatures.py' &

# # Run Gait Recognition 
gnome-terminal --disable-factory -- /bin/bash -c 'cd $PWD/gaitFeatures; cmake . ; make ; python3 src/gaitFeatures.py' &

# Run the main module 
gnome-terminal --disable-factory -- /bin/bash -c 'cd $PWD/multiModalHumanIdentification; cmake . ; make ; python3 src/multiModalHumanIdentification.py' &

# Run demo module

# If no parameter passed run CameraSimple from Harware
if [ "$#" -eq 0 ]; then
gnome-terminal --disable-factory -- /bin/bash -c 'cd $PWD/../../hardware/camera/camerasimple/; cmake . ; make ; python3 src/camerasimple.py' &   
video_path="CameraSimple"
else
video_path=$1
fi

echo "Running module on:$video_path in 10 seconds"
sleep 10

# Run the main module 
gnome-terminal --disable-factory -- /bin/bash -c "cd $PWD/test/humanIdentificationClient/; cmake . ; make ; python3 src/humanIdentificationClient.py --video-path $video_path; echo $video_path; sleep 100"