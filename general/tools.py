import os
import pickle


def save_data(path, fn, data):
    if os.path.isdir(path):
        with open(os.path.join(path,fn), 'wb') as f:
            pickle.dump(data, f)
    else:
        print('data save error')


def load_data(path, fn):
    if os.path.isfile(os.path.join(path, fn)):
        with open(os.path.join(path,fn), 'rb') as f:
            data = pickle.load(f)
    return data
