import numpy as np
import fcntl

def read_locations(file_path):
    with open(file_path, 'rb') as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        location_list = np.load(f, mmap_mode='r')
        fcntl.flock(f, fcntl.LOCK_UN)
    return location_list

# Read the locations
file_path = 'location_test.npy'
locations = read_locations(file_path)
locations.shape
