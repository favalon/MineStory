import os
import json
import numpy as np
from sklearn.cluster import KMeans

RECURSIVE_TIME = 1
MINI_SIMILAR = 0


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
    if scene_index == len(rep_scenes)-1:
        return

    new_path_list = []
    if scene_index == 0:
        for rep_scene in rep_scenes[scene_index]:
            new_path_list.append([rep_scene.tolist()])
    else:
        for path in path_list:
            for rep_scene in rep_scenes[scene_index]:
                new_path_list = path.append(rep_scene.tolist())

    cal_rep_path_collection(rep_scenes, new_path_list, scene_index+1)

    return new_path_list


def cal_selected_movie_path_collection(movies):
    for movie in movies:
        pass
    return 1


def tempo_result_output(candi_scene):
    candi_dict = {}
    for i, scene in enumerate(candi_scene):
        scene_candi_dict = {}
        for path in scene:
            path_class = ''.join(list(map(str, path)))

            if path_class in scene_candi_dict.keys():
                scene_candi_dict[path_class] += 1
            else:
                scene_candi_dict[path_class] = 1
        candi_dict[i] = scene_candi_dict
    print(json.dumps(candi_dict, indent=4, sort_keys=True))


def main(movies):
    get_scenes_tri(movies)

    rep_scenes, candi_scene = cal_rep_scenes_tri(movies)

    # =================== temp usage ==================
    tempo_result_output(candi_scene)
    # =================================================

    path_list = []
    rep_path = cal_rep_path_collection(rep_scenes, path_list, 0)

    selected_movie_path = cal_selected_movie_path_collection(movies)


    pass


if __name__ == '__main__':
    main()