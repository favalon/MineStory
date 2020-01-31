import os
import numpy as np
# if not FLAG_ALL_ROLE:
#     if character['rule'] == ACCESS_ROLE:
#         char_index, char_flag = get_status_flag(character)
#         project['{role}_flag'.format(role=character['rule'])] = {char_index: char_flag}

STATUS = ['health', 'mental_health', 'change', 'crisis', 'goal']


def story_first_process(project):
    flag = np.full((len(project['character_flag'].keys()), len(STATUS)), 1)
    for c_i in project['character_flag'].keys():
        for st_i, status in enumerate(STATUS):
            for s_i in range(1, len(project['scene'])):
                if s_i == len(project['scene'])-1 and project['scene'][s_i]['specify_data'][c_i][status] == project['scene'][s_i-1]['specify_data'][c_i][status]:
                    flag[c_i][st_i] = 0
                if project['scene'][s_i]['specify_data'][c_i][status] == project['scene'][s_i-1]['specify_data'][c_i][status]:
                    continue
                else:
                    break

        if 'story_first_character_flag' not in project:
            project['story_first_character_flag'] = {}
            char_class = flag[c_i].tolist()
            char_class = list(map(str, char_class))
            project['story_first_character_flag'][c_i] = ''.join(char_class)
        else:
            char_class = flag[c_i].tolist()
            char_class = list(map(str, char_class))
            project['story_first_character_flag'][c_i] = ''.join(char_class)

    pass


