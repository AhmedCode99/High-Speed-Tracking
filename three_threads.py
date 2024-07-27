import cv2
import numpy as np
import neoapi
import threading
import queue
import fcntl
from npy_append_array import NpyAppendArray
import psutil
import os
import time

# Camera Settings
camera = neoapi.Cam()  # Create camera object
camera.Connect('700006383766')  # Connect to camera
camera.f.ExposureTime.Set(20)  # Set exposure time
camera.f.Width.value = 48  # Set width
camera.f.Height.value = 48  # Set height
camera.f.OffsetY.value = 132  # Set OffsetY
camera.f.OffsetX.value = 512  # Set OffsetX
camera.f.Gain.value = 1  # Set Gain
camera.f.AcquisitionFrameRateEnable.value = True
camera.f.AcquisitionFrameRate.value = 8000  # fps
print("camera ok")

# Queues to hold frames and locations
frame_queue = queue.Queue()
location_queue = queue.Queue()
memory_list = []

def monitor_memory():
    pid = os.getpid()
    process = psutil.Process(pid)
    mem_info = process.memory_info()
    return mem_info.rss / (1024*1024)

def load_template(file_path):
    """
    Load a template from a file.
    
    Args:
        file_path (str): Path to the template file.
    
    Returns:
        tuple: A tuple containing the template (numpy array), height, and width.
    """
    template = np.load(file_path)
    h, w = template.shape
    return template, h, w

def capture_frames(frame_count):
    """
    Capture frames from the camera and put them into a queue.
    
    Args:
        frame_count (int): Number of frames to capture.
    """
    for _ in range(frame_count):
        frame = camera.GetImage().GetNPArray()  # Get Image as np.array
        frame_queue.put(frame)  # Save it in Queue
    frame_queue.put(None)  # Signal to the find thread that capturing is done

def find_location(template, frame_count):
    """
    Find the location of the template in each frame and put the locations into a queue.
    
    Args:
        template (numpy array): The template to match in frames.
        frame_count (int): Number of frames to process.
    """
    while True:
        frame = frame_queue.get()  # Get frame from queue
        if frame is None:  # Condition to exit the loop
            break
        result = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF)  # Perform template matching
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)  # Find location
        location_queue.put(min_loc)  # Add location to queue
    location_queue.put(None)  # Signal to the save thread that processing is done

def save_location(file_path, frame_count, batch_size=1000):
    """
    Save locations in batches to a file.
    
    Args:
        file_path (str): Path to the file where locations will be saved.
        batch_size (int): Number of locations per batch.
    
    Raises:
        ValueError: If frame_count is not a multiple of batch_size.
    """
    if frame_count % batch_size != 0:
        raise ValueError("Frame count must be a multiple of batch size")
    
    batch = []
    np.save(file_path, [[0, 0]])  # Create a file to save locations in
    i = 1
    while True:
        loc = location_queue.get()  # Get location from queue
        if loc is None:  # Condition to exit the loop
            break
        batch.append(loc)
        if len(batch) >= batch_size:
            loc_batch = np.array(batch)
            with open(file_path, 'r+b') as f:
                fcntl.flock(f, fcntl.LOCK_EX)  # Lock file
                f.close()  # Close the file handle before loading with mmap_mode
                location_list = np.load(file_path, mmap_mode='r+')
                location_list = np.concatenate((location_list, loc_batch), axis=0)
                with open(file_path, 'wb') as f:
                    np.save(f, location_list)
                    fcntl.flock(f, fcntl.LOCK_UN)  # Unlock file
            batch = []
            print('Batch {} Saved'.format(i))
            i = i+1
            rss_memory = monitor_memory()
            memory_list.append(rss_memory)
        location_queue.task_done()

def read_locations(file_path):
    """
    Reads a numpy array of locations from a specified file.

    This function opens a file in binary read mode, applies a shared lock to ensure 
    safe reading in a multi-process environment, loads the numpy array from the file 
    using memory mapping for efficient reading, and then unlocks the file before returning 
    the array.

    Parameters:
    file_path (str): The path to the file containing the numpy array of locations.

    Returns:
    numpy.ndarray: A numpy array containing the locations read from the file.

    """
    with open(file_path, 'rb') as f:  # Open File
        fcntl.flock(f, fcntl.LOCK_SH)  # Lock file
        location_list = np.load(f, mmap_mode='r')  # Read data in file
        fcntl.flock(f, fcntl.LOCK_UN)  # Unlock file
    return location_list


# Load template
template, h, w = load_template('template.npy')

# Number of frames to process
frame_count = 5000 #1500000
batch_size = 1000 #150000

# File Path for saving locations
file_path = 'location_test.npy'

# Create and start threads
capture_thread = threading.Thread(target=capture_frames, args=(frame_count,))
find_thread = threading.Thread(target=find_location, args=(template, frame_count))
save_thread = threading.Thread(target=save_location, args=(file_path, frame_count, batch_size))

capture_thread.start()
find_thread.start()
save_thread.start()

# Wait for threads to finish
capture_thread.join()
find_thread.join()
save_thread.join()

# Save Memory Usage
np.save('memory_usage.npy', memory_list)

# Disconnect the camera
camera.Disconnect()
print("camera disconnected")
