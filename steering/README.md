# The steering directory

This folder contains all the files to make the autonomous steering happen.

`exploring_steering_data.ipynb`, used to explore and examine the collected training data for the car steering, making sure the collected data is good and correct.

`convert_numpy_to_files.ipynb`, used to convert numpy arrays (images) to actual files saved in `/data`. This is not needed in any way, just used to quickly visualise the frames in the file explorer. The collected data fits into memory, no need to use image files.


`auto_steering_model_training.py` used to create and train the steering models.

`auto_steering_model.ipynb`, same as `auto_steering_model_training.py`, but in a notebook. Used for early testing of techniques such as data augmentation and to try different models in early stages to check feasibility before full number of epochs are used in `auto_steering_model_training.py`.

`analysing_models.ipynb`, used to analyise a model after training, such as loss/acc plots and displaying layer outputs. If needed, this is to be updated to make it easier to see all information at once.

`data_sequence.py`, data sequence class for data loading, processing, and to manage custom batches.