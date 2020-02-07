import numpy as np
import itertools
import matplotlib.pyplot as plt
from pathlib import Path
import json
from scipy import spatial


class Cluster:
    def __init__(self, cluster, project_id):
        self.cluster = cluster
        self.contain = [cluster]
        self.project_ids = [project_id]

    def update_cluster(self, cluster, p_id):
        self.contain.append(cluster)
        cluster_sum = np.zeros(cluster.shape)
        for _cluster in self.contain:
            cluster_sum += _cluster
        self.cluster = cluster_sum/len(self.contain)
        self.project_ids.append(p_id)

    def cluster_plot(self, status_index):
        marker = itertools.cycle((',', '+', '.', 'o', '*'))
        x = np.arange(0, len(self.cluster))
        for status in self.contain:
            plt.plot(x, status, c=np.random.rand(3, ), marker=next(marker))

        path_all_plot = "statistics_collection/plot_data/status_{st_id}/all_plot/".format(st_id=status_index)
        path_cluster_rep = "statistics_collection/plot_data/status_{st_id}/cluster_average_rep/".format(st_id=status_index)

        Path(path_all_plot)\
            .mkdir(parents=True, exist_ok=True)
        Path(path_cluster_rep)\
            .mkdir(parents=True, exist_ok=True)

        plt.title('Cluster ID:{cluster_id} Status:{status_index} Plot, {movie_num} Movies in this Cluster '
                  .format(cluster_id=self.project_ids[0], status_index=status_index, movie_num=len(self.project_ids)))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.ylim(0, 4)
        plt.savefig(path_all_plot + 'cluster_{cluster_id}_movies_status{status_index}.png'
                    .format(cluster_id=self.project_ids[0], status_index=status_index))

        plt.clf()
        plt.plot(x, self.cluster, c=np.random.rand(3, ), marker=next(marker))
        plt.title('Cluster ID:{cluster_id}, Status:{status_index} Representation Plot, '
                  '{movie_num} Movies in this Cluster'
                  .format(cluster_id=self.project_ids[0], status_index=status_index, movie_num=len(self.project_ids)))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.ylim(0, 4)
        plt.savefig(path_cluster_rep + 'cluster_{cluster_id}_rep_movies_status{status_index}.png'
                    .format(cluster_id=self.project_ids[0], status_index=status_index))
        plt.clf()

    def rep_cluster_plot(self, status_index):
        marker = itertools.cycle((',', '+', '.', 'o', '*'))
        x = np.arange(0, len(self.cluster))
        for status in self.contain:
            plt.plot(x, status, c=np.random.rand(3, ), marker=next(marker))

        path_best_rep = "statistics_collection/plot_data/status_{st_id}/best_rep/".format(st_id=status_index)
        Path(path_best_rep).mkdir(parents=True, exist_ok=True)

        plt.title('Cluster ID:{cluster_id} Status:{status_index} Plot '
                  .format(cluster_id=self.project_ids[0], status_index=status_index))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.ylim(0, 4)
        plt.savefig(path_best_rep+'cluster_{cluster_id}_movies_status{status_index}.png'
                    .format(cluster_id=self.project_ids[0], status_index=status_index))

        plt.clf()
        plt.plot(x, self.cluster, c=np.random.rand(3, ), marker=next(marker))
        plt.title('Cluster ID:{cluster_id}, Status:{status_index} Representation Plot, {movie_num} Movies in this Cluster'
                  .format(cluster_id=self.project_ids[0], status_index=status_index, movie_num=len(self.project_ids)))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.ylim(0, 4)
        plt.savefig(path_best_rep+'best_rep/cluster_{cluster_id}_rep_movies_status{status_index}.png'
                    .format(cluster_id=self.project_ids[0], status_index=status_index))
        plt.clf()


class MoviePlot:
    def __init__(self, p_id, p_name, main_char_index, movie_status, resample_status,normalize_axis):
        self.project_id = p_id
        self.project_name = p_name
        self.movie_status = movie_status
        self.x_axis = normalize_axis
        self.main_char_index = main_char_index
        self.resample_status = resample_status

        self.down_sample_status = None

    def down_sample(self, n=100):
        resample_len = self.resample_status.shape[-1]
        adder = int(resample_len/n)
        self.down_sample_status = np.zeros((self.resample_status.shape[0], self.resample_status.shape[1], n))
        for c_i in range(self.resample_status.shape[0]):
            for st_i in range(self.resample_status.shape[1]):
                pointer = 0
                for s_i in range(n):
                    # print(pointer)
                    self.down_sample_status[c_i][st_i][s_i] = self.resample_status[c_i][st_i][pointer]
                    pointer += adder


class Movie:
    def __init__(self, m_id, m_name, p_id, p_name, characters, main_char):
        self.m_id = m_id
        self.m_name = m_name
        self.p_id = p_id
        self.p_name = p_name
        self.characters = characters
        self.main_char = main_char

        self.scene_len = None
        self.status = None
        self.main_status = None
        self.path = None
        self.url = None
        self.initial_url()

    def initial_url(self):
        self.url = 'http://story.minestoryboard.com/#/SpecifyCharacters/{p_id}'.format(p_id=self.p_id)
        pass

    def initial_status(self, status):
        self.scene_len = status.shape[0]
        self.status = status

        self.main_status = status[:, self.main_char['index'], :]

    def initial_path(self):
        status = self.status
        path = np.empty((self.scene_len-1, len(self.characters)), dtype=object)
        for i in range(path.shape[0]):
            for c in range(path.shape[1]):
                _status_1 = self.status[i-1][c].tolist()
                _status_1 = list(map(str, _status_1))
                _status_2 = self.status[i][c].tolist()
                _status_2 = list(map(str, _status_2))
                # _path = ''.join(_status_1) + '_' + ''.join(_status_2)
                _path = (''.join(_status_1), ''.join(_status_2))
                path[i][c] = _path
        self.path = path


class MoviesAnalysis:
    def __init__(self, movies):
        self.movies = movies

        self.n_status = {}
        self.n_path = {}
        self.separate_char_dict = {}

        self._cal_n_status_path()

    def status_path_all_freq(self):
        pass

    def separate_char_strict(self):
        separate_main_char = {}

        # main_char_index = get_mainChar_index()
        main_char_index = 0
        for movie in self.movies:
            movie_id = movie.p_id
            main_char_class = self._char_class(movie, main_char_index)
            main_status = movie.status[:, main_char_index, :]

            if main_char_class in separate_main_char.keys():
                separate_main_char[main_char_class].append(movie)
            else:
                separate_main_char[main_char_class] = []
                separate_main_char[main_char_class].append(movie)

        self.separate_char_dict = separate_main_char

    def separate_char_story(self):
        pass

    def separate_char_status_strict(self):
        if len(self.separate_char_dict.keys()) < 1:
            return
        separate_status_freq = {}
        separate_path_freq = {}
        separate_status_num = []
        separate_path_num = []
        for key in self.separate_char_dict.keys():
            movies = self.separate_char_dict[key]
            status_freq = {}
            path_freq = {}
            for movie in movies:
                # main_char_index = get_mainChar_index(movie)
                char_index = [0]
                self._count_status_freq(movie, char_index, status_freq)
                self._count_path_freq(movie, char_index, path_freq)
                separate_status_freq[key] = status_freq
                separate_path_freq[key] = path_freq

                for status_key in status_freq.keys():
                    if status_key in separate_status_num:
                        continue
                    else:
                        separate_status_num.append(status_key)

                for path_key in path_freq.keys():
                    if path_key in separate_path_num:
                        continue
                    else:
                        separate_path_num.append(path_key)

        return separate_status_freq, separate_path_freq, separate_status_num, separate_path_num

    def separate_char_status_story(self):
        pass

    def _count_status_freq(self, movie, char_index, status_freq):
        for s in movie.status:
            for c in char_index:
                _status = s[c].tolist()
                _status = list(map(str, _status))
                _status = ''.join(_status)
                if _status in status_freq.keys():
                    status_freq[_status] = status_freq[_status] + 1
                else:
                    status_freq[_status] = 1

    def _count_path_freq(self, movie, char_index, path_freq):
        for i in range(1, movie.status.shape[0]):
            for c in char_index:
                _status_1 = movie.status[i - 1][c].tolist()
                _status_1 = list(map(str, _status_1))
                _status_2 = movie.status[i][c].tolist()
                _status_2 = list(map(str, _status_2))
                if _status_1 == _status_2:
                    continue
                _path = ''.join(_status_1) + '_' + ''.join(_status_2)
                if _path in path_freq.keys():
                    path_freq[_path] = path_freq[_path] + 1
                else:
                    path_freq[_path] = 1
        pass

    def _char_class(self, movie, char_index):
        char = movie.characters[char_index]

        char_class = '{health}{attitude}{change}{crisis}{goal}'\
            .format(health=char['flag_health'], attitude=char['flag_mental_health'],
                    change=char['flag_change'], crisis=char['flag_crisis'],
                    goal=char['flag_goal'])
        return char_class

    def _cal_n_status_path(self):
        for movie in self.movies:
            status = movie.status
            save_status(status, self.n_status, len(movie.characters))
            get_path(status, self.n_path)

# Support


def save_status(status, n_status, char_num):
    empty_count = 0
    for i in range(char_num):
        count = 0
        for j in range(status.shape[0]):
            machee = status[j][i]
            matcher = np.array([9, 9, 9, 9, 9])
            if np.array_equal(machee, matcher):
                count += 1
            if j == status.shape[0] - 1 and count - 1 == j:
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
            _status_1 = status[i - 1][c].tolist()
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