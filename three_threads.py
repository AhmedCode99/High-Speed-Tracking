import cv2
import numpy as np
import neoapi
import threading
import queue
import fcntl

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
camera.f.AcquisitionFrameRate.value = 5000  # fps
print("camera ok")

# Queues to hold frames and locations
frame_queue = queue.Queue()
location_queue = queue.Queue()

# Function to load template
def load_template(file_path):
    template = np.load(file_path)
    h, w = template.shape
    return template, h, w

# Function to capture frames
def capture_frames(frame_count):
    for _ in range(frame_count):
        frame = camera.GetImage().GetNPArray()
        frame_queue.put(frame)
    frame_queue.put(None)  # Signal to find thread that capturing is done

# Function to find location
def find_location(template, frame_count):
    while True:
        frame = frame_queue.get()
        if frame is None:
            break
        result = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        location_queue.put(min_loc)
    location_queue.put(None)  # Signal to save thread that processing is done

# Function to save location in batches
def save_location(file_path, batch_size=1000):
    if frame_count % batch_size != 0:
        raise ValueError("Frame count must be a multiple of batch size")
    batch = []
    np.save(file_path, [[0, 0]])  # Create a file to save locations in
    i = 1
    while True:
        loc = location_queue.get()
        if loc is None:
            break
        batch.append(loc)
        if len(batch) >= batch_size:
            loc_batch = np.array(batch)
            with open(file_path, 'r+b') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.close()  # Close the file handle before loading with mmap_mode
                location_list = np.load(file_path, mmap_mode='r+')
                location_list = np.concatenate((location_list, loc_batch), axis=0)
                with open(file_path, 'wb') as f:
                    np.save(f, location_list)
                    fcntl.flock(f, fcntl.LOCK_UN)
            batch = []
            print('batch {} saved'.format(i))
            i = i + 1
        location_queue.task_done()

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
