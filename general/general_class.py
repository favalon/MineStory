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
        self.path = None
        self.url = None
        self.initial_url()

    def initial_url(self):
        self.url = 'http://story.minestoryboard.com/#/SpecifyCharacters/{p_id}'.format(p_id=self.p_id)
        pass

    def initial_status(self, status):
        self.scene_len = status.shape[0]
        self.status = status
        pass

    def initial_path(self):
        status = self.status
        pass


class MoviesData:
    def __init__(self, status, path):
        self.status = status
        self.path = path

    def initial_any(self):
        pass

