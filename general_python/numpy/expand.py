import numpy as np
max_length=512
x = np.array([1, 2, 3, 4, 5])
x = np.expand_dims(x, axis=0) if x.ndim == 1 else x
if x.shape[1] < max_length:
    padding_size = max_length - x.shape[1]
    x = np.pad(x, [(0, 0), (0, padding_size)], mode='constant', constant_values=0)