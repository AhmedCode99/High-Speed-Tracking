import numpy as np
import fcntl
from utility_functions import read_locations

# Read the locations
file_path = 'location_test.npy'
locations = read_locations(file_path)
locations.shape
