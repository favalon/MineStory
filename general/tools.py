import os
import pickle
import urllib.request
import json
from collections import namedtuple


def get_data_url(url):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    # data = json.loads(response.read(), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    return data


def get_data_json(path):
    if os.path.isfile(path):
        with open(os.path.join(path)) as f:
            data = json.load(f)
    return data


def get_data_txt(path):
    if os.path.isfile(path):
        with open(path, 'r') as f:
            data = f.readlines()
    return data


def save_data(path, fn, data):
    if os.path.isdir(path):
        with open(os.path.join(path, fn), 'wb') as f:
            pickle.dump(data, f)
    else:
        print('data save error')


def load_data(path, fn):
    if os.path.isfile(os.path.join(path, fn)):
        with open(os.path.join(path,fn), 'rb') as f:
            data = pickle.load(f)
    return data
