import os
import json
import numpy as np
from sklearn.cluster import KMeans
from scipy import spatial
from general.tools import save_data_json
from datetime import date


RECURSIVE_TIME = 1
STATUS_WEIGHT = [1, 1, 1, 1, 2]


def cal_movie_scenes_class_num(epoch):
    num = 3
    while epoch > 0:
        num += 2**epoch
        epoch -= 1
    return num


def get_status_class(movie, scene_index, char_index):
    _status = [0, 0, 0, 0, 0]
    _statuses = movie['scene'][scene_index]['specify_data'][char_index]
    char_class = movie['story_first_character_flag'][char_index]
    _status[0] = _statuses['health']
    _status[1] = _statuses['mental_health']
    _status[2] = _statuses['change']
    _status[3] = _statuses['crisis']
    _status[4] = _statuses['goal']

    # temp disable check
    # for i, c in enumerate(char_class):
    #     if c == '0':
    #         _status[i] = 9

    return _status


def find_tri_scenes_class(char_index, start, end, movie, scenes_class, sc_start, sc_end, epoch):
    if epoch == 0:
        return
    else:
        mid = int((start + end) / 2)
        s_st = get_status_class(movie, start, char_index)
        m_st = get_status_class(movie, mid, char_index)
        e_st = get_status_class(movie, end, char_index)

        sc_mid = int((sc_start + sc_end) / 2)
        if epoch == 1:
            scenes_class[sc_start] = s_st
            scenes_class[sc_end] = e_st

        scenes_class[sc_mid] = m_st

    find_tri_scenes_class(char_index, start, mid, movie, scenes_class, sc_start, sc_mid, epoch-1)
    find_tri_scenes_class(char_index, mid, end, movie, scenes_class, sc_mid, sc_end, epoch-1)


def get_scenes_tri(movies):
    num = int(cal_movie_scenes_class_num(RECURSIVE_TIME-1))

    for movie in movies:
        movie_scenes_class = [None] * num
        # char_index = get_char_index(movie, role)
        char_index = 0
        find_tri_scenes_class(char_index, 0, len(movie['scene'])-1, movie,
                              movie_scenes_class, 0, (num-1), RECURSIVE_TIME)
        movie['scene_tri'] = movie_scenes_class


# cal representation status for all selected movies
def cal_rep_scenes_tri(movies):

    scenes_tri = []
    for movie in movies:
        scenes_tri.append(movie['scene_tri'])

    rep_scenes = []
    candi_scenes = []
    for s_i in range(len(scenes_tri[0])):
        candi_scene = []
        for m_i in range(len(scenes_tri)):
            candi_scene.append(scenes_tri[m_i][s_i])
        candi_scenes.append(candi_scene)
        kmeans = KMeans(n_clusters=4, init='k-means++', max_iter=300, n_init=10, random_state=0)
        pred_y = kmeans.fit_predict(np.array(candi_scene))
        rep_scene = kmeans.cluster_centers_
        rep_scenes.append(rep_scene)

    return rep_scenes, candi_scenes


def cal_rep_path_collection(rep_scenes, path_list, scene_index):
    if scene_index == len(rep_scenes):
        return path_list

    new_path_list = []
    if scene_index == 0:
        for rep_scene in rep_scenes[scene_index]:
            new_path_list.append([rep_scene.tolist()])
    else:
        for i in range(len(path_list)):
            for rep_scene in rep_scenes[scene_index]:
                new_path = path_list[i].copy()
                new_path.append(rep_scene.tolist())
                new_path_list.append(new_path)

    return cal_rep_path_collection(rep_scenes, new_path_list, scene_index+1)



def cal_selected_movie_path_collection(movies):
    movie_path_dict = {}
    for movie in movies:
        movie_path_dict[movie['id']] = movie['scene_tri']
    return movie_path_dict


def tempo_result_output(candi_scene):
    candi_dict = {}
    temp_candi_path =[]
    for i, scene in enumerate(candi_scene):
        scene_candi_dict = {}
        temp_candi = []
        for path in scene:
            path_class = ''.join(list(map(str, path)))

            if path_class in scene_candi_dict.keys():
                scene_candi_dict[path_class] += 1
            else:
                scene_candi_dict[path_class] = 1
                temp_candi.append(path)
        candi_dict[i] = scene_candi_dict
        temp_candi_path.append(np.array(temp_candi))
    print(json.dumps(candi_dict, indent=4, sort_keys=True))
    return temp_candi_path


def cal_node_distance(movie_node, rep_node):
    cost = 0
    for i in range(len(movie_node)):
        cost += abs(movie_node[i] - rep_node[i]) * STATUS_WEIGHT[i]

    return cost


def select_n_path(movie_path, rep_path_dict, n):
    rank_path_dict = {}
    for rep_id in rep_path_dict.keys():
        rep_path = rep_path_dict[rep_id]
        cos_sim = 0
        for i, rep_node in enumerate(rep_path):
            cos_sim += cal_node_distance(movie_path[i], rep_node)
        rank_path_dict[rep_id] = cos_sim
    ranked_path_dict = {k: v for k, v in sorted(rank_path_dict.items(), key=lambda item: item[1])}

    n_path = []
    for rep_id in ranked_path_dict.keys():
        if n < 1:
            break
        one_path = [[round(y) for y in x] for x in rep_path_dict[rep_id]]
        n_path.append(one_path)
        n -= 1
    return n_path


def select_n_best_similarity(selected_movie_path, rep_path, n):
    rep_path_dict = {}
    for i, path in enumerate(rep_path):
        rep_path_dict[i] = path

    movie_hyper_path_dict = {}
    for movie_id in selected_movie_path.keys():
        movie_hyper_path = select_n_path(selected_movie_path[movie_id], rep_path_dict, n)
        movie_hyper_path_dict[movie_id] = movie_hyper_path

    return movie_hyper_path_dict


def main(movies, n=10):
    get_scenes_tri(movies)

    rep_scenes, candi_scene = cal_rep_scenes_tri(movies)

    # =================== temp usage ==================
    temp_candi_scene = tempo_result_output(candi_scene)
    # =================================================

    path_list = []
    # wait update rep_scenes selections
    # rep_path = cal_rep_path_collection(rep_scenes, path_list, 0)

    rep_path = cal_rep_path_collection(temp_candi_scene, path_list, 0)

    selected_movie_path = cal_selected_movie_path_collection(movies)

    movie_hyper_path_dict = select_n_best_similarity(selected_movie_path, rep_path, n)

    for key in selected_movie_path.keys():
        selected_movie_path[key] = [''.join(list(map(str, x))) for x in selected_movie_path[key]]
    for key in movie_hyper_path_dict.keys():
        movie_hyper_path_dict[key] = [[''.join(list(map(str, y))) for y in x] for x in movie_hyper_path_dict[key]]
    today = date.today()
    save_data_json('statistics_collection/data_{}'.format(today), 'select_movie_path.json', selected_movie_path)
    save_data_json('statistics_collection/data_{}'.format(today), 'hyper_movie_path.json', movie_hyper_path_dict)

    pass


if __name__ == '__main__':
    main()