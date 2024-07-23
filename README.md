# High-Speed-Tracking

## Introduction
The purpose of this repository is to provide a method to track a moving object and be able to access the location in real-time. The OpenCV template matching method is utilized for object tracking. For the sake of efficiency, the code run is three threads. The first thread collects frames from the camera, the second thread detects the location of the object in each thread, and the third thread saves the object locations to a `.npy` file in your local device. You can access the object locations in real-time.

## How to use the code
### Saving the data
An example of how to use this code is in the main branch of this repository in `how_to_run_code.py`.
1. The camera is connected and the camera settings are adjusted to get a good image of the object being tracked.
2. Two queues are started, one to hold the frames from the camera, and another to hold the location of the object
3. The template is imported via the `load_template` function.
4. Determine the number of frames to be captured and processed.
5. Determine how often location data will be saved locally.
6. Determine file path for saving locations, if the file does not exist then it will be automatically created.
7. Each thread is created using the `threading.Thread(target=, args=())`
8. Each thread is started via `.start()`
9. Threads are stopped via '.join()`
10. The camera is disconnected
### Reading the Data in Real Time
If you wish to read the data while the locations are being collected, simply use the `read_locations` function, an example is shown in `how_to_access_locations.py`.
### Possible Issues
1. If the file chosen to save the data already exists, then the new data will overwrite the old data.
2. The code assumes that all images are in grayscale.
3. Batch size must be a multiple of the number of frames to be collected.
