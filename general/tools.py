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
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.isdir(path):
        with open(os.path.join(path, fn), 'wb') as f:
            pickle.dump(data, f)
    else:
        print('data save error')


def save_data_json(path, fn, data):
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.isdir(path):
        with open(os.path.join(path, fn), 'w') as f:
            json.dump(data, f, indent=2)
    else:
        print('data save error')


def load_data(path, fn):
    if os.path.isfile(os.path.join(path, fn)):
        with open(os.path.join(path,fn), 'rb') as f:
            data = pickle.load(f)
    return data


def summary_save(movies, n_status, path, today):
    save_data('statistics_collection/data_{}'.format(today), 'movies_data', movies)
    save_data('statistics_collection/data_{}'.format(today), 'n_status', n_status)
    save_data('statistics_collection/data_{}'.format(today), 'path', path)


def summary_print(char_class, status_num, path_num, status, path, today):
    print("=========== Data: {} ==============".format(today))
    print("======== Using Character Class : {char_class} ==========".format(char_class=char_class))
    print("number of n ={sn}, number of path={pn}".format(sn=status_num, pn=path_num))
    print("================== Status Start =====================")
    print("first level key : activate flag (health，attitude to goal, change，crisis, goal), "
          "0 is deactivate, 1 is activate")
    print("second level key : level value (health，attitude to goal， change，crisis, goal)")
    print(json.dumps(status, indent=4, sort_keys=True))
    print("================== Status   End =====================")

    print("================== Path Start =====================")
    print("first level key : activate flag (health，attitude to goal，change，crisis，goal), 0 is deactivate, 1 is activate")
    print("second level key : path value (status1_status_2)")
    print(json.dumps(path, indent=4, sort_keys=True))
    print("================== Path End =====================")