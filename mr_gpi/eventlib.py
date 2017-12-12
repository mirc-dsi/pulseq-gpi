import numpy as np


class EventLibrary:
    def __init__(self):
        # size of data is 0x0 because of range_len in find()
        self.keys, self.data, self.lengths, self.type = {}, {}, {}, {}

    def __str__(self):
        s = "EventLibrary:"
        s += "\nkeys: " + str(len(self.keys))
        s += "\ndata: " + str(len(self.data))
        s += "\nlengths: " + str(len(self.lengths))
        s += "\ntype: " + str(len(self.type))
        return s

    def find(self, new_data):
        found = False
        key_id = 0

        try:
            range_len = len(self.data)
        except ValueError:
            range_len = 0
        for i in range(1, range_len + 1):
            if self.lengths[i] == max(new_data.shape) and np.linalg.norm((self.data[i] - new_data), ord=2) < 1e-6:
                key_id, found = self.keys[i], True
                return [key_id, found]

        key_id = 1 if (len(self.keys) == 0) else (max(self.keys) + 1)
        return [key_id, found]

    def insert(self, key_id, new_data, data_type):
        if not isinstance(new_data, np.ndarray):
            new_data = np.array(new_data)
        self.keys[key_id] = key_id
        self.data[key_id] = new_data
        self.lengths[key_id] = max(self.data[key_id].shape)
        self.type[key_id] = data_type
