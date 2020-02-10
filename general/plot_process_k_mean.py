import numpy as np
import random
import os
import glob
from scipy.interpolate import interp1d
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import spatial
import itertools
from general.tools import save_data, load_data, clear_folders

from general.general_class import MoviePlot, Cluster

STATUS_NUM = 5
STATUS_MAX_LENGTH = 1000
MIN_THRESHOLD = 5


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


def prepare_movie_plot_data(movies, n, access_role, save=False):
    movies_plot = {}
    for movie in movies:
        project_id = movie['id']
        project_name = movie['name']
        char_num = len(movie['character_flag'])
        if '{}_flag'.format(access_role) not in movie.keys():
            continue
        main_char_index = list(movie['{}_flag'.format(access_role)].keys())

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
        movie_plot.down_sample_strict(n=n)
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
    dist = np.linalg.norm(np.abs(cluster1-cluster2))
    # dist = 1 - spatial.distance.cosine(cluster1, cluster2)
    return dist


def compare_cluster(status_cluster, movie_status, project_id, char_index, status, edc_dis):

    if len(status_cluster) == 0:
        for c_i in char_index:
            status_cluster.append(Cluster(movie_status[c_i][status], project_id))
    else:
        for c_i in char_index:
            cluster_flag = False
            dist_list = []
            for i, cur_cluster in enumerate(status_cluster):
                dist = cal_error_distance(cur_cluster.cluster, movie_status[c_i][status])
                if dist <= edc_dis:
                    dist_list.append(dist)
                    cluster_flag = True
                else:
                    dist_list.append(999)
            if cluster_flag:
                index = np.argmin(dist_list)
                status_cluster[index].update_cluster(movie_status[c_i][status], project_id)

            else:
                status_cluster.append(Cluster(movie_status[c_i][status], project_id))


# find target cluster number
def movies_status_cluster(movies_plot, status, min_threshold=10, n_clusters=25):
    status_cluster = {}
    status_list = []
    project_id_list = []

    for p_i in movies_plot.keys():
        movie_plot = movies_plot[p_i]
        movie_status = movie_plot.down_sample_status
        char_index = movie_plot.main_char_index
        for c_i in char_index:
            cur_status = movie_status[c_i][status]
            status_list.append(cur_status)
            project_id_list.append(p_i)
        # compare_cluster(status_cluster, movie_status, p_i, char_index, status, min_threshold)
    kmeans = KMeans(n_clusters=n_clusters)
    X = np.array(status_list)
    kmeans.fit(X)
    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_

    for i, p_id in enumerate(project_id_list):
        movie_plot = movies_plot[p_id]
        char_index = movie_plot.main_char_index
        movie_status = movie_plot.down_sample_status
        for c_i in char_index:
            if labels[i] not in status_cluster.keys():
                status_cluster[labels[i]] = Cluster(movie_status[c_i][status], p_id)
                # status_cluster[labels[i]].update_average_cluster(centroids[labels[i]])
            else:
                status_cluster[labels[i]].update_cluster(movie_status[c_i][status], p_id)
    return status_cluster, min_threshold


def split_cluster_group(status_cluster, status_index):
    cluster_group = {}
    for key in status_cluster.keys():
        cls = status_cluster[key]
        if len(cls.project_ids) < 3:
            if "0_2" not in cluster_group.keys():
                cluster_group['0_2'] = []
                cluster_group['0_2'].append(cls)
            else:
                cluster_group['0_2'].append(cls)
        if 3 <= len(cls.project_ids) < 9:
            if "3_8" not in cluster_group.keys():
                cluster_group['3_8'] = []
                cluster_group['3_8'].append(cls)
            else:
                cluster_group['3_8'].append(cls)
        if 9 <= len(cls.project_ids):
            if "9_n" not in cluster_group.keys():
                cluster_group['9_n'] = []
                cluster_group['9_n'].append(cls)
            else:
                cluster_group['9_n'].append(cls)

    path_cluster_group = "statistics_collection/plot_data/status_{st_id}/cluster_group/".format(st_id=status_index)
    Path(path_cluster_group).mkdir(parents=True, exist_ok=True)
    path_cluster_group_data = "statistics_collection/plot_data/status_{st_id}/cluster_group_data/".format(st_id=status_index)
    Path(path_cluster_group_data).mkdir(parents=True, exist_ok=True)

    cls_keys = list(cluster_group.keys())
    marker = itertools.cycle((',', '+', '.', 'o', '*'))
    color = itertools.cycle(('b', 'g', 'r', 'c', 'm', 'y', 'k'))

    for cls_group in cls_keys:
        x = np.arange(len(cluster_group[cls_group][0].cluster))
        if len(cluster_group[cls_group]) > 5:
            part_len = int(len(cluster_group[cls_group]) / 2 + 0.5)
        else:
            part_len = 5
        split_cls_keys = [cluster_group[cls_group][x:x+part_len]
                          for x in range(0, len(cluster_group[cls_group]), part_len)]
        part = 0
        for cls_keys in split_cls_keys:
            for cls in cls_keys:
                plt.plot(x, cls.cluster, c=next(color),
                        linewidth=2.0, label='cl_id:{}, m_num:{}'
                         .format(cls.project_ids[0], len(cls.project_ids)))
            plt.title('Cluster movies number range {m_range}'
                      .format(m_range=cls_group))
            plt.xlabel('time')
            plt.ylabel('level')
            plt.ylim(0, 4)
            plt.legend(loc="upper left")
            plt.savefig(path_cluster_group + 'cluster_movie_range{m_range}_part{part}.png'
                        .format(m_range=cls_group, part=part))
            plt.clf()
            save_data(path_cluster_group_data, 'cluster_{}_data'.format(cls_group), cluster_group)
            part += 1


def plot_main(movies, n=10,  access_role='MainCharacter', n_clusters=25, cluster_plt=False, project_id=None, all_movie=False):
    # movies_plot = prepare_movie_plot_data(movies, n, access_role, save=True)
    movies_plot = load_data('statistics_collection/data/', 'movie_plot')

    movies_plot[118].down_sample_strict(n=11)
    movies_plot[118].plot_status(down_sample=False, char_index=[0, 1], st_index=[[4, 3, 1, 2, 0], [4, 3]])
    movies_plot[118].print_status_guide(char_index=[0, 1], st_index=[[4, 3, 1, 2, 0], [4, 3]])
    pass

    # selected_statues = [0, 1, 2, 3, 4]
    # for status in selected_statues:
    #     clear_folders("statistics_collection/plot_data/status_{st_id}/*/*".format(st_id=status))
    #     status_cluster, edc_dis = movies_status_cluster(movies_plot, status, n_clusters=n_clusters)
    #     print("distance threshold for status {st_id} is {dis_th}, number of cluster {cls_num}"
    #           .format(st_id=status, dis_th=edc_dis, cls_num=len(status_cluster)))
    #
    #     if all_movie:
    #         plot_all(movies_plot, status)
    #     elif project_id is not None:
    #         plot_by_id(movies_plot, project_id, status)
    #     elif cluster_plt:
    #         for cls in status_cluster.keys():
    #             status_cluster[cls].cluster_plot(status)
    #             status_cluster[cls].head_ranked_plot(status)
    #
    #         # the cluster contains most movies
    #         # status_cluster[0].rep_cluster_plot(status)
    #
    #         split_cluster_group(status_cluster, status)
    #
    #     else:
    #         print("plot args wrong")
    #     pass
