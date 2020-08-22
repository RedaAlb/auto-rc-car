# The steering directory

This directory contains all the files for the autonomous steering/driving.

`exploring_steering_data.ipynb`, used to explore and examine the collected training data for the car steering, making sure the collected data is as expected.

`convert_numpy_to_files.ipynb`, used to convert numpy arrays (images) to actual files saved in `/data`. This is not needed in any way, just used to quickly visualise the frames in the file explorer. The collected data fits into memory, no need to use image files. However, if you are running on a system that cannot fit the data into memory, use this.


`auto_steering_model.ipynb`, used to create and train the steering models.

`analyse_model.ipynb`, used to analyise a model after training, such as loss/acc plots, visualising layer outputs, and looking at which samples were predicted wrong.

`expand_data_samples.ipynb`, is used to increase the number of samples in three ways:
- Excract left and right samples from a secondary source and add it to a main data source (fill1).
- Flip right and left samples to generate double amount of left and right samples in the main data source (fill2).
- Combining two data sources.

`data_sequence.py`, data sequence class for data loading, processing, and to manage custom batches.

`auto_steering_handler.py`, used to handle the autonomous driving by using the trained models.


