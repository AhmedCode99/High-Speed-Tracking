import cv2
import numpy as np
import neoapi
import threading
import queue
import fcntl

# Initialize queues
frame_queue = queue.Queue()
location_queue = queue.Queue()

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

def save_location(file_path, batch_size=1000):
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
        location_queue.task_done()
