# The sign detection directory

This directory contains everything needed for the sign detection and recognition.

`circle.py`, used to create circle instances of detected circles(potential signs) in the frame.

`circle_detector.py`, used to detect the circles in the frame.

`sign_detector.py`, handles the detection and the recognition of signs using the trained sign detection model `trained_sign_recognition_model.h5`

`sign_names.csv`, stores the class id and name of each sign.

`sign_recognition_model.ipynb`, used to create and train the sign recognition model.

`trained_sign_recognition_model.h5`, trained sign detection classifier model.

`/data`, the traffic signs data can be downloaded from [here](https://bitbucket.org/jadslim/german-traffic-signs/src/master/) if needed.