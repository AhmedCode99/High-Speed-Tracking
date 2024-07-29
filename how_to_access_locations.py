import numpy as np
import fcntl

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
        fcntl.flock(f, fcntl.LOCK_EX)  # Lock file
        location_list = np.load(f, mmap_mode='r')  # Read data in file
        fcntl.flock(f, fcntl.LOCK_UN)  # Unlock file
    return location_list


# Read the locations
file_path = 'location_test.npy'
locations = read_locations(file_path)
locations.shape
