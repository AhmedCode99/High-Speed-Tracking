# Function to load template
def load_template(file_path):
    template = np.load(file_path)
    h, w = template.shape
    return template, h, w

# Function to capture frames
def capture_frames(frame_count):
    for _ in range(frame_count):
        frame = camera.GetImage().GetNPArray() # Get Image as np.array
        frame_queue.put(frame) # Save it in Queue
    frame_queue.put(None)  # Signal to find thread that capturing is done

# Function to find location
def find_location(template, frame_count):
    while True:
        frame = frame_queue.get() # Get frame from queue
        if frame is None: # Condition to exit the loop
            break
        result = cv2.matchTemplate(frame, template, cv2.TM_SQDIFF) # "Convolution"
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result) # Find Location
        location_queue.put(min_loc) # Add location to queue
    location_queue.put(None)  # Signal to save thread that processing is done

# Function to save location in batches
def save_location(file_path, batch_size=1000):
    if frame_count % batch_size != 0:
        raise ValueError("Frame count must be a multiple of batch size")
    batch = []
    np.save(file_path, [[0, 0]])  # Create a file to save locations in
    
    while True:
        loc = location_queue.get() # Get location from queue
        if loc is None: # Condition to exit the loop
            break
        batch.append(loc)
        if len(batch) >= batch_size:
            loc_batch = np.array(batch)
            with open(file_path, 'r+b') as f:
                fcntl.flock(f, fcntl.LOCK_EX) # Lock file
                f.close()  # Close the file handle before loading with mmap_mode
                location_list = np.load(file_path, mmap_mode='r+')
                location_list = np.concatenate((location_list, loc_batch), axis=0)
                with open(file_path, 'wb') as f:
                    np.save(f, location_list)
                    fcntl.flock(f, fcntl.LOCK_UN) # Unlock file
            batch = []
        location_queue.task_done()
