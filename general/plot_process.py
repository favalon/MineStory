import numpy as np
import random
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import itertools
from general.tools import save_data, load_data

from general.general_class import MoviePlot, Cluster

STATUS_NUM = 5
STATUS_MAX_LENGTH = 1000
MIN_THRESHOLD = 7


def resample_scene_length(movie_status, resampled_movie_status, scene_len):
    single_occ = int(STATUS_MAX_LENGTH/scene_len)
    addition_occ = STATUS_MAX_LENGTH%scene_len
    for c_i in range(movie_status.shape[0]):
        for st_i in range(movie_status.shape[1]):
            addition_occ_p = 0
            start = 0
            for s_i in range(movie_status.shape[2]):
                end = start + single_occ
                if addition_occ_p < addition_occ:
                    end += 1
                resampled_movie_status[c_i][st_i][start:end] = movie_status[c_i][st_i][s_i]
                start = end
                addition_occ_p += 1
    return


def prepare_movie_plot_data(movies, save=False):
    movies_plot = {}
    for movie in movies:
        project_id = movie['id']
        project_name = movie['name']
        char_num = len(movie['character_flag'])
        main_char_index = list(movie['MainCharacter_flag'].keys())

        # health, mental_health, change, crisis, goal
        movie_status = np.zeros((char_num, STATUS_NUM, len(movie['scene'])))
        resampled_movie_status = np.zeros((char_num, STATUS_NUM, STATUS_MAX_LENGTH))
        for c_i in movie['character_flag'].keys():
            for i, scene in enumerate(movie['scene']):
                movie_status[int(c_i)][0][i] = scene['specify_data'][int(c_i)]['health']
                movie_status[int(c_i)][1][i] = scene['specify_data'][int(c_i)]['mental_health']
                movie_status[int(c_i)][2][i] = scene['specify_data'][int(c_i)]['change']
                movie_status[int(c_i)][3][i] = scene['specify_data'][int(c_i)]['crisis']
                movie_status[int(c_i)][4][i] = scene['specify_data'][int(c_i)]['goal']

        resample_scene_length(movie_status, resampled_movie_status, len(movie['scene']))

        normalize_status_x = np.arange(movie_status.shape[-1], dtype=np.float32)
        normalize_status_x /= np.max(np.abs(normalize_status_x))
        movie_plot = MoviePlot(project_id, project_name, main_char_index, movie_status, resampled_movie_status, normalize_status_x)
        movie_plot.down_sample(n=100)
        movies_plot[project_id] = movie_plot
        if save:
            save_data('statistics_collection/data/', 'movie_plot', movies_plot)
    return movies_plot


def plot_all(movies, status):
    count_max = 5
    count = 0
    plt_index = 0
    marker = itertools.cycle((',', '+', '.', 'o', '*'))
    for p_id in movies.keys():
        x = movies[p_id].x_axis
        for c_i in movies[p_id].main_char_index:
            y = movies[p_id].movie_status[int(c_i)][status]
            # if y[-1] == 3:
            #     # print(movies[p_id].project_id)
            #     print(movies[p_id].project_name)
            if sum(y) == len(x)*9 or sum(y) == 0:
                print(movies[p_id].project_id)
                continue
            plt.plot(x, y, c=np.random.rand(3,), marker=next(marker))
            count += 1

            if count == count_max:
                plt.title('All Movies Status {status_id} Plot '.format(status_id=status))
                plt.xlabel('time')
                plt.ylabel('level')
                plt.savefig('statistics_collection/plot_data/all_movies_status{status_index}_part{plt_index}.png'
                            .format(status_index=status, plt_index=plt_index))
                plt_index += 1
                count = 0
                plt.clf()


    # plt.title('The Lasers in Three Conditions')
    # plt.xlabel('row')
    # plt.ylabel('column')
    # plt.legend()
    # plt.show()


def random_color():
    rgbl=[255,0,0]
    random.shuffle(rgbl)
    return tuple(rgbl)


def plot_by_id(movies, project_id, status):
    if status is not None:
        for p_id in project_id:
            x = movies[p_id].x_axis
            for c_i in movies[p_id].main_char_index:
                y = movies[p_id].movie_status[int(c_i)][status]
                if sum(y) == len(x) * 9 or sum(y) == 0:
                    continue
                plt.plot(x, y, 'r--')
        plt.title('Movies Status {status_id} Plot '.format(status_id=status))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.savefig('statistics_collection/plot_data/movies_status{status_index}.png'.format(status_index=status))
    else:
        print("plot status is wrong")
    pass


def cal_error_distance(cluster1, cluster2):
    dist = np.linalg.norm(cluster1-cluster2)
    return dist


def compare_cluster(status_cluster, movie_status, project_id, char_index, status):

    if len(status_cluster) == 0:
        for c_i in char_index:
            status_cluster.append(Cluster(movie_status[c_i][status], project_id))
    else:
        for c_i in char_index:
            cluster_flag = False
            dist_list = []
            for i, cur_cluster in enumerate(status_cluster):
                dist = cal_error_distance(cur_cluster.cluster, movie_status[c_i][status])
                if dist <= MIN_THRESHOLD:
                    dist_list.append(dist)
                    cluster_flag = True
                else:
                    dist_list.append(999)
            if cluster_flag:
                index = np.argmin(dist_list)
                status_cluster[index].update_cluster(movie_status[c_i][status], project_id)

            else:
                status_cluster.append(Cluster(movie_status[c_i][status], project_id))


def movies_status_cluster(movies_plot, status):
    status_cluster = []
    for p_i in movies_plot.keys():
        movie_plot = movies_plot[p_i]
        movie_status = movie_plot.down_sample_status
        char_index = movie_plot.main_char_index
        compare_cluster(status_cluster, movie_status, p_i, char_index, status)
    return status_cluster


def plot_main(movies, cluster_plt=False, project_id=None, status=None, all_movie=False):
    # movies_plot = prepare_movie_plot_data(movies, save=False)
    movies_plot = load_data('statistics_collection/data/', 'movie_plot')

    status_cluster = movies_status_cluster(movies_plot, status)

    if all_movie:
        plot_all(movies_plot, status)
    elif project_id is not None:
        plot_by_id(movies_plot, project_id, status)
    elif cluster_plt:
        for cls in status_cluster:
            cls.cluster_plot(status)
    else:
        print("plot args wrong")
    pass
