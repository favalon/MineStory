import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

from general.general_class import MoviePlot

STATUS_NUM = 5


def prepare_movie_plot_data(movies):
    movies_plot = {}
    for movie in movies:
        project_id = movie['id']
        project_name = movie['name']
        char_num = len(movie['character_flag'])
        main_char_index = list(movie['MainCharacter_flag'].keys())

        # health, mental_health, change, crisis, goal
        movie_status = np.zeros((char_num, STATUS_NUM, len(movie['scene'])))
        for c_i in movie['character_flag'].keys():
            for i, scene in enumerate(movie['scene']):
                movie_status[int(c_i)][0][i] = scene['specify_data'][int(c_i)]['health']
                movie_status[int(c_i)][1][i] = scene['specify_data'][int(c_i)]['mental_health']
                movie_status[int(c_i)][2][i] = scene['specify_data'][int(c_i)]['change']
                movie_status[int(c_i)][3][i] = scene['specify_data'][int(c_i)]['crisis']
                movie_status[int(c_i)][4][i] = scene['specify_data'][int(c_i)]['goal']

        normalize_status_x = np.arange(movie_status.shape[-1], dtype=np.float32)
        normalize_status_x /= np.max(np.abs(normalize_status_x))
        movie_plot = MoviePlot(project_id, project_name, main_char_index, movie_status, normalize_status_x)
        movies_plot[project_id] = movie_plot
    return movies_plot


def plot_all(movies, status):

    for p_id in movies.keys():
        x = movies[p_id].x_axis
        for c_i in movies[p_id].main_char_index:
            y = movies[p_id].movie_status[int(c_i)][status]
            if y[-1] == 3:
                # print(movies[p_id].project_id)
                print(movies[p_id].project_name)
            if sum(y) == len(x)*9 or sum(y) == 0:
                continue
            plt.plot(x, y, 'r--')
            # print(m_i)
    plt.title('All Movies Status {status_id} Plot '.format(status_id=status))
    plt.xlabel('time')
    plt.ylabel('level')
    plt.savefig('statistics_collection/plot_data/all_movies_status{status_index}.png'.format(status_index=status))

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


def plot_main(movies, project_id=None, status=None, all_movie=False):
    movies_plot = prepare_movie_plot_data(movies)
    if all_movie:
        plot_all(movies_plot, status)
    elif project_id is not None:
        plot_by_id(movies_plot, project_id, status)
    else:
        print("plot args wrong")
    pass
