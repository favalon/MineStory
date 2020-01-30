import urllib.request
import numpy as np
import json
import os
from general.general_class import Movie, MoviesAnalysis
from general.tools import save_data, load_data


KEY_CHARACTER_NUM = 5
CHARACTER_STATUS_NUM = 5

# USE_PROJECT_ID = [17, 19, 20, 22, 28, 31, 34, 43, 44, 45, 46, 47, 48, 49, 50,51, 29, 65, 66, 70, 71]


def get_data_url(url):
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data


def get_data_json(path):
    if os.path.isfile(path):
        with open(os.path.join(path)) as f:
            data = json.load(f)
    return data


def get_char_index(characters):
    index_list = []
    for character in characters:
        index_list.append(character['index'])
    return index_list


def get_status(scene, char_index_list):
    status = np.zeros((len(scene), KEY_CHARACTER_NUM, CHARACTER_STATUS_NUM*2), dtype=int)
    for i, s in enumerate(scene):
        for c_i in char_index_list:
            char_status = s['specify_data'][c_i]
            status[i][c_i][0] = char_status['health']
            status[i][c_i][1] = char_status['mental_health']
            status[i][c_i][2] = char_status['change']
            status[i][c_i][3] = char_status['crisis']
            status[i][c_i][4] = char_status['goal']
            status[i][c_i][5] = char_status['default_health']
            status[i][c_i][6] = char_status['default_mental_health']
            status[i][c_i][7] = char_status['default_change']
            status[i][c_i][8] = char_status['default_crisis']
            status[i][c_i][9] = char_status['default_goal']
    return status


def correct_status(status, char_num):
    # KEY_CHARACTER_NUM = char_num
    status_re = np.zeros((status.shape[0], KEY_CHARACTER_NUM, CHARACTER_STATUS_NUM), dtype=int)
    status_re[0] = status[0, :, 0:CHARACTER_STATUS_NUM]
    for i in range(1, status.shape[0]):
        for c_i in range(KEY_CHARACTER_NUM):
            for s_i in range(CHARACTER_STATUS_NUM):
                if status[i][c_i][s_i+CHARACTER_STATUS_NUM] == 2:
                    status_re[i][c_i][s_i] = status_re[i-1][c_i][s_i]
                else:
                    status_re[i][c_i][s_i] = status[i][c_i][s_i]

    for j in range(status_re.shape[1]):
        for k in range(status_re.shape[2]):
            count = 1
            for i in range(1, status_re.shape[0]):

                if status_re[i][k][j] == status_re[i-1][k][j]:
                    count += 1
                if count == status_re.shape[0] and status_re[i][k][j] == status_re[i-1][k][j]:
                    status_re[:, k, j] = 9

    return status_re[:, :char_num, :]


def save_status(status, n_status, char_num):
    empty_count = 0
    for i in range(char_num):
        count = 0
        for j in range(status.shape[0]):
            machee = status[j][i]
            matcher = np.array([9, 9, 9, 9, 9])
            if np.array_equal(machee, matcher):
                count += 1
            if j == status.shape[0]-1 and count-1 == j:
                empty_count -= count

    for s in status:
        for i in range(char_num):
            c = s[i]
#        for c in s:
            l = c.tolist()
            l = list(map(str, l))
            _status = ''.join(l)

            if _status in n_status.keys():
                n_status[_status] = n_status[_status] + 1
            else:
                n_status[_status] = 1

    if '99999' in n_status.keys():
        n_status['99999'] = n_status['99999'] + empty_count


def get_path(status, path):
    for i in range(1, status.shape[0]):
        for c in range(status.shape[1]):
            _status_1 = status[i-1][c].tolist()
            _status_1 = list(map(str, _status_1))
            _status_2 = status[i][c].tolist()
            _status_2 = list(map(str, _status_2))
            if _status_1 == _status_2:
                continue
            _path = ''.join(_status_1) + '_' + ''.join(_status_2)
            if _path in path.keys():
                path[_path] = path[_path] + 1
            else:
                path[_path] = 1


def get_n_and_path(scene, char_index_list, n_status, path):
    status = get_status(scene, char_index_list)
    status = correct_status(status, len(char_index_list))
    save_status(status, n_status, len(char_index_list))
    get_path(status, path)
    # pass


def cal_status(scene, char_index_list):
    status = get_status(scene, char_index_list)
    status = correct_status(status, len(char_index_list))
    return status


def temp_modify(status):
    new_status_all = {}
    for char_class in status.keys():
        for _status in status[char_class].keys():
            new_class = ['1', '1', '1', '1', '1']
            for i, c in enumerate(_status):
                if c == '9':
                    new_class[i] = '0'
            new_class = ''.join(new_class)

            if new_class not in new_status_all:
                new_status_all[new_class] = {}
                new_status_all[new_class][_status] = status[char_class][_status]
            else:
                new_status_all[new_class][_status] = status[char_class][_status]

    return new_status_all


def general_process(data):
    # n_status = {}
    # path = {}
    #
    # movies_data = []

    # for movie in data:
    #     # if movie['id'] not in USE_PROJECT_ID:
    #     #     continue
    #     if movie['movie'] == None:
    #         continue
    #     movie_name = movie['movie']['name']
    #     char_index_list = get_char_index(movie['movie']['specify']['key_characters'])
    #     # char_index_list = [0, 1, 2, 3, 4]
    #     scene = movie['scene']
    #     if len(scene) < 2:
    #         continue
    #     # print(movie['id'])
    #     cur_movie = Movie(movie['movie']['id'], movie['movie']['name'], movie['id'], movie['name'],
    #                       movie['movie']['specify']['key_characters'], movie['movie']['specify']['key_characters'][0])
    #
    #     # status
    #     cur_movie_status = cal_status(scene, char_index_list)
    #     cur_movie.initial_status(cur_movie_status)
    #
    #     # path
    #     cur_movie.initial_path()
    #     movies_data.append(cur_movie)
    #     get_n_and_path(scene, char_index_list, n_status, path)

    movies_data = load_data('statistics_collection/data', 'movies_data')
    movieAnalysis = MoviesAnalysis(movies_data)
    movieAnalysis.separate_char()
    status_freq, path_freq, status_num, path_num = movieAnalysis.separate_char_status()

    # =========== temp status modify ==============
    status_freq = temp_modify(status_freq)

    save_data('statistics_collection/data', 'movies_data', movies_data)
    # save_data('/home/dl/MineStory/statistics_collection/data', 'n_status', n_status)
    # save_data('/home/dl/MineStory/statistics_collection/data', 'path', path)
    summary_print("Main", status_num, path_num, status_freq, path_freq)
    return


def summary_print(char_class, status_num, path_num, status, path):
    print("======== Using Character Class : {char_class} ==========".format(char_class=char_class))
    print("number of n ={sn}, number of path={pn}".format(sn=len(status_num), pn=len(path_num)))
    print("================== Status Start =====================")
    print("first level key : activate flag (health，attitude to goal，change，crisis，goal), 0 is deactivate, 1 is activate")
    print("second level key : level value (health，attitude to goal，change，crisis，goal)")
    print(json.dumps(status, indent=4, sort_keys=True))
    print("================== Status   End =====================")

    print("================== Path Start =====================")
    print("first level key : activate flag (health，attitude to goal，change，crisis，goal), 0 is deactivate, 1 is activate")
    print("second level key : path value (status1_status_2)")
    print(json.dumps(path, indent=4, sort_keys=True))
    print("================== Path End =====================")


def main():
    # data_url = "http://api.minestoryboard.com/get_projects_data"
    # data = get_data_url(data_url)
    # data = get_data_json('statistics_collection/data/or_data.json')
    # general_process(data)

    general_process("1")

    pass


if __name__ == '__main__':
    main()
