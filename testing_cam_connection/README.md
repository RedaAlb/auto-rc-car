# Testing camera network connection

This directory is used to test and analyse the camera network connection between the computer and the Raspberry Pi.

`testing_cam_connection.py`, used to test the camera connection and to obtain data about the connection, which is then used to visualise the connection using `cam_data_plots.ipynb`.


# Results

![network connection results](/readme_data/net_conn_results.png)

Each connection is established for 10 minutes. To keep the results fair and consistent, the camera was pointed to a screen that was running the same video for each experiment. This also ensured that image sizes were different rather than a static view/frame transmitted.

The bars represent a lost frame. We can see that for both 30 FPS and 60 FPS for all resolutions ~99% of the frames were successfully transferred. However, for the largest resolution (1640x922), for both 30 FPS and 60 FPS, the average FPS that the frames were received at was ~30.  After investigating this further, it was found that there was an average of 30 ms delay for the higher resolution compared to the 15 ms delay for the two lower resolutions, this explains why a 30 FPS is achieved. Because of the large size of the frame, it takes longer to send all the image bytes even though 99% of the frames were successfully  received. Despite this, 30 FPS is still not a terrible result for that high resolution.

More details can be found in the [paper](/readme_data/MSc_AI_Auto_RC_Car_paper.pdf) (page 7).