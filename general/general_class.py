import numpy as np
import json


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


class MoviesData:
    def __init__(self, movies):
        self.movies = movies

    def status_path_all_freq(self):
        pass

    def separate_main_char(self):
        pass

