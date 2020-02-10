import numpy as np
import itertools
import matplotlib.pyplot as plt
from pathlib import Path
from general.tools import getIndexPositions
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

    def update_average_cluster(self, cluster):
        self.cluster = cluster

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
        plt.savefig(path_best_rep+'cluster_{cluster_id}_rep_movies_status{status_index}.png'
                    .format(cluster_id=self.project_ids[0], status_index=status_index))
        plt.clf()

    def head_ranked_plot(self, status_index):
        head_num = 4
        marker = itertools.cycle((',', '+', '.', 'o', '*'))
        x = np.arange(0, len(self.cluster))
        for i, status in enumerate(self.contain):
            if i < head_num:
                plt.plot(x, status, c=np.random.rand(3, ), label='movies_id:{}'.format(self.project_ids[i]))

        plt.plot(x, self.cluster, c=np.random.rand(3, ), marker='o', linewidth=3.0, label='average')

        path_head_rep = "statistics_collection/plot_data/status_{st_id}/head_rep/".format(st_id=status_index)
        Path(path_head_rep).mkdir(parents=True, exist_ok=True)

        plt.title('Cluster ID:{cluster_id}, Status:{status_index} Representation Plot, {movie_num} Movies in this Cluster'
                  .format(cluster_id=self.project_ids[0], status_index=status_index, movie_num=len(self.project_ids)))
        plt.xlabel('time')
        plt.ylabel('level')
        plt.ylim(0, 4)
        plt.legend()
        plt.savefig(path_head_rep+'{m_num}_cluster_{cluster_id}_rep_movies_status{status_index}.png'
                    .format(m_num=len(self.project_ids),  cluster_id=self.project_ids[0], status_index=status_index))
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

    def down_sample_strict(self, n=100):
        resample_len = self.resample_status.shape[-1]
        adder = int(resample_len/n)
        self.down_sample_status = np.zeros((self.resample_status.shape[0], self.resample_status.shape[1], n))
        for c_i in range(self.resample_status.shape[0]):
            for st_i in range(self.resample_status.shape[1]):
                cur_status = self.resample_status[c_i][st_i].tolist()
                turing_point_y = []
                turing_point_x = []
                for i, st in enumerate(cur_status):
                    if i == 0:
                        turing_point_x.append(0)
                        turing_point_y.append(st)
                    else:
                        if cur_status[i-1] != st:
                            turing_point_x.append(i / (len(cur_status) - resample_len%n))
                            turing_point_y.append(st)

                if len(turing_point_x) > n:
                    print('n < turning point, unable to down sample {}, try other n'.format(self.project_id))
                    return
                fit_turning_point = [-1 for x in range(n)]
                fited_turing_point = [(False, 0) for x in range(n)]
                priority_order = []

                turing_point_y_rank = list(set(turing_point_y))
                start = 0
                end = len(turing_point_y_rank) - 1
                while True:
                    if len(priority_order) == len(turing_point_y_rank):
                        break
                    priority_order.append(turing_point_y_rank[end])
                    end -= 1
                    if len(priority_order) == len(turing_point_y_rank):
                        break
                    priority_order.append(turing_point_y_rank[start])
                    start += 1
                    if len(priority_order) == len(turing_point_y_rank):
                        break

                for lvl in priority_order:
                    if lvl not in turing_point_y:
                        continue
                    lv_index = getIndexPositions(turing_point_y, lvl)
                    for i in lv_index:
                        index = int(turing_point_x[i] * 10 + 0.5)
                        if not fited_turing_point[index][0]:
                            fit_turning_point[index] = turing_point_y[i]
                            fited_turing_point[index] = (True, turing_point_x[i])
                        elif turing_point_x[i] > fited_turing_point[index][1] and not fited_turing_point[index+1][0]:
                            fit_turning_point[index+1] = turing_point_y[i]
                            fited_turing_point[index+1] = (True, turing_point_x[i])
                        elif turing_point_x[i] < fited_turing_point[index][1] and not fited_turing_point[index-1][0]:
                            fit_turning_point[index - 1] = turing_point_y[i]
                            fited_turing_point[index - 1] = (True, turing_point_x[i])

                pointer = 0
                for s_i in range(n):
                    pointer += adder
                    if not fited_turing_point[s_i][0]:
                        self.down_sample_status[c_i][st_i][s_i] = self.resample_status[c_i][st_i][pointer]
                    else:
                        self.down_sample_status[c_i][st_i][s_i] = fit_turning_point[s_i]
            print(self.down_sample_status[c_i][st_i])

    def print_status_guide(self, char_index, st_index=None):
        labels = ['H', 'A', 'F', 'C', 'G']

        for s_i in range(1, self.down_sample_status.shape[-1]):
            print('=== Scene {s_i} Status change Guide ==='.format(s_i=s_i))
            for c_i in char_index:
                start_status = []
                end_status = []
                select_status = []
                for st_i in st_index[c_i]:
                    select_status.append(labels[st_i])
                    start_status.append(str(int(self.down_sample_status[c_i][st_i][s_i-1])))
                    end_status.append(str(int(self.down_sample_status[c_i][st_i][s_i])))
                guide = 'Character {c_i}\n' \
                        'status: {s_s}\n' \
                        'start:  {start}\n' \
                        'end:    {end}\n'\
                    .format(c_i=c_i, s_s=' '.join(select_status)
                            , start=' '.join(start_status), end=' '.join(end_status))
                print(guide)

    def plot_status(self, char_index, down_sample=False, st_index=None):
        if down_sample:
            sample_status = self.down_sample_status
            names = 'down_sample'
        else:
            sample_status = self.movie_status
            names = 'original'
        labels = ['health', 'attitude', 'change', 'crisis', 'goal']

        if st_index is not None:
            st_index_range = st_index
        else:
            st_index_range = [4, 3, 1, 2, 0]


        color = ['r', 'g', 'k', 'navy', 'm']
        marker = itertools.cycle((',', '+', '.', 'o', '*'))
        visual_bias = [0.06, 0.03, 0, -0.03, -0.06]
        line_style = ['-', '--', '-.', ':', 'dashdot']

        for c_i in char_index:
            x = np.arange(0, sample_status.shape[-1])
            fig, ax = plt.subplots()
            for st_i in st_index[c_i]:
                status = sample_status[c_i][st_i]
                c = color[st_i]
                ax.scatter(x, status+visual_bias[st_i], s=10, c=c)
                ax.plot(x, status+visual_bias[st_i], c=c, label=labels[st_i])
                # if down_sample:
                #     for i, value in enumerate(status):
                #         ax.annotate(value, (x[i], status[i]))

            path_single_movie_plot = "statistics_collection/plot_data/single_movie/{p_id}/{sample}/"\
                .format(sample=names, p_id=self.project_id)
            Path(path_single_movie_plot).mkdir(parents=True, exist_ok=True)
            plt.title(
                'Character : {char_index} Status : {st_range}'
                .format(char_index=c_i, st_range=', '.join([str(x) for x in st_index_range])))

            if down_sample:
                ax.set_xticks(x)
            plt.xlabel('time')
            plt.ylabel('level')
            plt.ylim(-0.5, 4.5)
            plt.xlim(-0.5, len(x))
            plt.legend()
            # if down_sample:
            plt.grid()
            plt.savefig(path_single_movie_plot + '{p_id}_{char_index}_'
                        .format(p_id=self.project_id, char_index=c_i))
            plt.clf()


        if down_sample:
            x = np.arange(0, sample_status.shape[-1])
            for s_i in range(1, len(x)):
                for c_i in char_index:
                    fig, ax1 = plt.subplots(figsize=(6, 10))
                    for st_i in st_index[c_i]:
                        status = sample_status[c_i][st_i]
                        c = color[st_i]
                        part_status = status[s_i-1:s_i+1]
                        part_x = x[s_i-1:s_i+1]
                        ax1.set_xticks(part_x)
                        plt.scatter(part_x, part_status+visual_bias[st_i], s=20, c=c)
                        plt.plot(part_x, part_status+visual_bias[st_i], label=labels[st_i])
                        for i, value in enumerate(part_status):
                            ax1.annotate(value, (part_x[i], part_status[i]), fontsize=30)
                    plt.title('Scene {}'.format(s_i), fontsize=50)
                    plt.xlabel('time', fontsize=30)
                    plt.ylabel('level', fontsize=30)
                    plt.xticks(fontsize=30)
                    plt.yticks(fontsize=30)
                    plt.ylim(-0.5, 4.5)
                    plt.xlim(part_x[0] - 0.5, part_x[-1] + 0.5)
                    plt.legend(fontsize=30)
                    plt.grid()
                    plt.savefig(path_single_movie_plot + '{p_id}_{char_index}_scene{s_i}'
                                .format(p_id=self.project_id, char_index=c_i, s_i=s_i))
                    plt.clf()
                    plt.close()


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