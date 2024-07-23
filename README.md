# High-Speed-Tracking

## Introduction
This repository provides a method to track a moving object and access its location in real time using the OpenCV template matching method. To ensure efficiency, the code runs in three threads:
1. The first thread collects frames from the camera.
2. The second thread detects the location of the object in each frame.
3. The third thread saves the object locations to a `.npy` file on your local device, allowing real-time access to the object locations.

## How to Use the Code

### Saving the Data
An example of how to use this code can be found in the main branch of this repository in `how_to_run_code.py`.

1. **Connect the Camera:**
   - Connect the camera and adjust the settings to get a good image of the object being tracked.

2. **Initialize Queues:**
   - Start two queues: one to hold the frames from the camera, and another to hold the location of the object.

3. **Load the Template:**
   - Import the template using the `load_template` function.

4. **Set Parameters:**
   - Determine the number of frames to be captured and processed.
   - Decide how often location data will be saved locally.
   - Specify the file path for saving locations. If the file does not exist, it will be automatically created.

5. **Create Threads:**
   - Create each thread using `threading.Thread(target=, args=())`.

6. **Start Threads:**
   - Start each thread using `.start()`.

7. **Stop Threads:**
   - Stop the threads using `.join()`.

8. **Disconnect the Camera:**
   - Disconnect the camera when done.

### Reading the Data in Real Time
To read the data while locations are being collected, use the `read_locations` function. An example is provided in `how_to_access_locations.py`.

### Possible Issues
1. **Overwriting Data:**
   - If the file chosen to save the data already exists, the new data will overwrite the old data.

2. **Image Format:**
   - The code assumes that all images are in grayscale.

3. **Batch Size:**
   - The batch size must be a multiple of the number of frames to be collected.

This repository provides a comprehensive solution for real-time object tracking using OpenCV, ensuring efficient and effective tracking through multi-threading.
