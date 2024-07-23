import cv2
import numpy as np
import neoapi
import threading
import queue
import fcntl
from utility_functions import load_template, capture_frames, find_location, save_location

# Camera Settings
camera = neoapi.Cam()  # Create camera object
camera.Connect('700006383766')  # Connect to camera
camera.f.ExposureTime.Set(20)  # Set exposure time
camera.f.Width.value = 48  # Set width
camera.f.Height.value = 48  # Set height
camera.f.OffsetY.value = 231  # Set OffsetY
camera.f.OffsetX.value = 304  # Set OffsetX
camera.f.Gain.value = 1  # Set Gain
camera.f.AcquisitionFrameRateEnable.value = True
camera.f.AcquisitionFrameRate.value = 8000  # fps
print("camera ok")

# Queues to hold frames and locations
frame_queue = queue.Queue()
location_queue = queue.Queue()

# Load template
template, h, w = load_template('template.npy')

# Number of frames to process
frame_count = 1500000

# Create and start threads
capture_thread = threading.Thread(target=capture_frames, args=(frame_count,))
find_thread = threading.Thread(target=find_location, args=(template, frame_count))
save_thread = threading.Thread(target=save_location, args=('location_test.npy', 150000))

capture_thread.start()
find_thread.start()
save_thread.start()

# Wait for threads to finish
capture_thread.join()
find_thread.join()
save_thread.join()

# Disconnect the camera
camera.Disconnect()
print("camera disconnected")
