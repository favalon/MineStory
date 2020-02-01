import urllib.request
import numpy as np
import json
import os
from general.general_class import Movie, MoviesAnalysis
from general.tools import save_data, load_data, get_data_url, get_data_txt, get_data_json, save_data_json
from general.tools import summary_save, summary_print
from general.single_movie_process import story_first_process
from greed_process.main import main as greed_process
from datetime import date
from collections import namedtuple

ACCESS_ROLE = 'MainCharacter'

FLAG_ALL_ROLE = False


def force_modify(movie):
    pass


def get_status_flag(character):
    character_index = character['index']
    character_class_flag = '{health}{attitude}{change}{crisis}{goal}' \
        .format(health=character['flag_health'], attitude=character['flag_mental_health'],
                change=character['flag_change'], crisis=character['flag_crisis'],
                goal=character['flag_goal'])
    return character_index, character_class_flag


def correct_scene_data(scenes, character):
    # ========= clean data base on flag information ============
    for i, scene in enumerate(scenes):
        s_c_i = character['index']
        if character['flag_health'] == 0:
            scenes[i]['specify_data'][s_c_i]['health'] = 9
        if character['flag_mental_health'] == 0:
            scenes[i]['specify_data'][s_c_i]['mental_health'] = 9
        if character['flag_change'] == 0:
            scenes[i]['specify_data'][s_c_i]['change'] = 9
        if character['flag_crisis'] == 0:
            scenes[i]['specify_data'][s_c_i]['crisis'] = 9
        if character['flag_goal'] == 0:
            scenes[i]['specify_data'][s_c_i]['goal'] = 9


def single_process(project):
    characters = project['movie']['specify']['key_characters']
    for character in characters:
        correct_scene_data(project['scene'], character)
        if not FLAG_ALL_ROLE:
            if character['rule'] == ACCESS_ROLE:
                char_index, char_flag = get_status_flag(character)
                project['{role}_flag'.format(role=character['rule'])] = {char_index: char_flag}
        char_index, char_flag = get_status_flag(character)
        if 'character_flag' in project.keys():
            project['character_flag'][char_index] = char_flag
        else:
            project['character_flag'] = {char_index:char_flag}
            # project['character_flag'][char_index] = char_flag


def count_each_char_status(n_status_class, char_index, movie):
    value = [0, 0, 0, 0, 0]
    for scene in movie['scene']:
        _statuses = scene['specify_data'][char_index]
        value[0] = _statuses['health']
        value[1] = _statuses['mental_health']
        value[2] = _statuses['change']
        value[3] = _statuses['crisis']
        value[4] = _statuses['goal']

        story_first_status = movie['story_first_character_flag'][char_index]
        for i, c in enumerate(story_first_status):
            if c == '0':
                value[i] = 9

        _status = '{health}{attitude}{change}{crisis}{goal}'\
            .format(health=value[0], attitude=value[1],
                    change=value[2], crisis=value[3], goal=value[4])
        if _status not in n_status_class.keys():
            n_status_class[_status] = 1
        else:
            n_status_class[_status] += 1


def count_each_char_path(n_path_class, char_index, movie):
    value_1 = [0, 0, 0, 0, 0]
    value_2 = [0, 0, 0, 0, 0]
    for s_i in range(1, len(movie['scene'])):
        _statuses_1 = movie['scene'][s_i-1]['specify_data'][char_index]
        value_1[0] = _statuses_1['health']
        value_1[1] = _statuses_1['mental_health']
        value_1[2] = _statuses_1['change']
        value_1[3] = _statuses_1['crisis']
        value_1[4] = _statuses_1['goal']

        _statuses_2 = movie['scene'][s_i]['specify_data'][char_index]
        value_2[0] = _statuses_2['health']
        value_2[1] = _statuses_2['mental_health']
        value_2[2] = _statuses_2['change']
        value_2[3] = _statuses_2['crisis']
        value_2[4] = _statuses_2['goal']

        story_first_status = movie['story_first_character_flag'][char_index]
        for i, c in enumerate(story_first_status):
            if c == '0':
                value_1[i] = 9
                value_2[i] = 9

        if value_1 == value_2:
            continue

        _status = '{health1}{attitude1}{change1}{crisis1}{goal1}_{health2}{attitude2}{change2}{crisis2}{goal2}'\
            .format(health1=value_1[0], attitude1=value_1[1],
                    change1=value_1[2], crisis1=value_1[3], goal1=value_1[4],
                    health2=value_2[0], attitude2=value_2[1],
                    change2=value_2[2], crisis2=value_2[3], goal2=value_2[4])
        if _status not in n_path_class.keys():
            n_path_class[_status] = 1
        else:
            n_path_class[_status] += 1


def count_each_char_3_path(n_3_path_class, char_index, movie):
    value_1 = [0, 0, 0, 0, 0]
    value_2 = [0, 0, 0, 0, 0]
    value_3 = [0, 0, 0, 0, 0]

    for s_i in range(2, len(movie['scene'])):
        _statuses_1 = movie['scene'][s_i-2]['specify_data'][char_index]
        value_1[0] = _statuses_1['health']
        value_1[1] = _statuses_1['mental_health']
        value_1[2] = _statuses_1['change']
        value_1[3] = _statuses_1['crisis']
        value_1[4] = _statuses_1['goal']

        _statuses_2 = movie['scene'][s_i-1]['specify_data'][char_index]
        value_2[0] = _statuses_2['health']
        value_2[1] = _statuses_2['mental_health']
        value_2[2] = _statuses_2['change']
        value_2[3] = _statuses_2['crisis']
        value_2[4] = _statuses_2['goal']

        _statuses_3 = movie['scene'][s_i]['specify_data'][char_index]
        value_3[0] = _statuses_3['health']
        value_3[1] = _statuses_3['mental_health']
        value_3[2] = _statuses_3['change']
        value_3[3] = _statuses_3['crisis']
        value_3[4] = _statuses_3['goal']

        story_first_status = movie['story_first_character_flag'][char_index]
        for i, c in enumerate(story_first_status):
            if c == '0':
                value_1[i] = 9
                value_2[i] = 9
                value_3[i] = 9

        if value_1 == value_2 == value_3:
            continue

        _status = '{health1}{attitude1}{change1}{crisis1}{goal1}_{health2}{attitude2}{change2}{crisis2}{goal2}' \
                  '_{health3}{attitude3}{change3}{crisis3}{goal3}'\
            .format(health1=value_1[0], attitude1=value_1[1],
                    change1=value_1[2], crisis1=value_1[3], goal1=value_1[4],
                    health2=value_2[0], attitude2=value_2[1],
                    change2=value_2[2], crisis2=value_2[3], goal2=value_2[4],
                    health3=value_3[0], attitude3=value_3[1],
                    change3=value_3[2], crisis3=value_3[3], goal3=value_3[4]
                    )
        if _status not in n_3_path_class.keys():
            n_3_path_class[_status] = 1
        else:
            n_3_path_class[_status] += 1


def count_status_path(movie, n_status, n_path, n_3_path):
    # char_index = movie['MainCharacter_flag'].keys()[0]
    chars_index = [0]
    for char_index in chars_index:
        char_class = ''.join(movie['story_first_character_flag'][char_index])

        if char_class not in n_status.keys():
            n_status[char_class] = {}
            count_each_char_status(n_status[char_class], char_index, movie)
        else:
            count_each_char_status(n_status[char_class], char_index, movie)

        if char_class not in n_path.keys():
            n_path[char_class] = {}
            count_each_char_path(n_path[char_class], char_index, movie)
        else:
            count_each_char_path(n_path[char_class], char_index, movie)

        if char_class not in n_3_path.keys():
            n_3_path[char_class] = {}
            count_each_char_3_path(n_3_path[char_class], char_index, movie)
        else:
            count_each_char_3_path(n_3_path[char_class], char_index, movie)

    pass


def general_process(movies):
    # ===== movie first data clean ===========
    filtered_movies = []
    for movie in movies:
        if not movie['movie'] or movie['id'] in [57, 58, 63, 82, 78, 62, 61, 59, 54, 50, 41, 40, 55, 64, 74, 72]:
            continue
        filtered_movies.append(movie)

    for movie in filtered_movies:
        # print(movie['id'])
        force_modify(movie)
        single_process(movie)

    # ===== story manager first (smf) data ===========
    movies_smf = filtered_movies
    for movie in movies_smf:
        story_first_process(movie)

    return movies, movies_smf


def count_process(movies_smf, today):
    # ===== count process ===========

    n_status = {}
    n_path = {}
    n_3_path = {}
    n_status_num = 0
    n_path_num = 0
    n_3_path_num = 0
    for movie in movies_smf:
        count_status_path(movie, n_status, n_path, n_3_path)

    for st in n_status:
        n_status_num += len(n_status[st])
    for pt in n_path:
        n_path_num += len(n_path[pt])
    for p3t in n_3_path:
        n_3_path_num += len(n_3_path[p3t])

    summary_print('MainCharacter', n_status_num, n_path_num, n_status, n_path, today)
    # summary_save(movies_smf, n_status, n_path,  today)
    print(n_3_path_num)
    print(json.dumps(n_3_path, indent=4, sort_keys=True))


def temp_movie_modify_process(movie, main_char_index):
    for scene in movie['scene']:
        scene['specify_data'][main_char_index]['health'] = scene['specify_data'][main_char_index]['crisis']


def greed_path_process(movies, today):
    selected_class = ['11111', '01111']
    selected_movies = []
    for movie in movies:
        # main_char_index = get_main_character_index()
        main_char_index = 0
        if movie['story_first_character_flag'][main_char_index] in selected_class:
            # =================== temp usage ==================
            if movie['story_first_character_flag'][main_char_index] in ['01111']:
                temp_movie_modify_process(movie, main_char_index)
            # =================================================
            selected_movies.append(movie)

    save_data_json('statistics_collection/data_{}'.format(today), 'movies_data', selected_movies)

    greed_process(selected_movies, n=10)

    pass


def main():
    today = date.today()

    # data_url = "http://api.minestoryboard.com/get_projects_data"
    # data = get_data_url(data_url)

    data = get_data_json('statistics_collection/data/movies_20200130')

    movies, movies_smf = general_process(data)
    # count_process(movies_smf, today)

    greed_path_process(movies_smf, today)


if __name__ == '__main__':
    main()