# Original Project Data
You can directly obtain the data by the url:  http://api.minestoryboard.com/get_projects_data

because we still keep update/delete the data day to day. You can directly use the local data copy.\
Data copy (2020/1/29) path: statistics_collection/data/or_data.json 

The data is a list of dictionaries, each dictionary (*project_i*) represent a movie project in the stroy manager tool.\

## project_i
- 'id' : int, project id
- 'name' : str, project name
- 'movie' : dict, project movie information
- 'scene' : list, data in each scene in order

### movie (dict):
- 'id' : int ,movie id
- 'name' : str, movie name in the movie manager
- 'specify' : dict, movie infroamtion detail
  - 'key_characters' : list, key character information\
    - key_characters[*i*] : dict, key character *i* setting
      - 'id': int, 
      - 'value': str, character name
      - 'name' : str, 
      - 'specify_id' : int, 
      - 'flag_health' : int, 1 or 0 represent *Health* available to this character or not.
      - 'flag_mental_health' : int, 1 or 0 represent *Attitude Toward Goal* available to this character or not.
      - 'falg_goal' : int, 1 or 0 represent *Goal* available to this character or not.
      - 'flag_change' : int, 1 or 0 represent *Change* available to this character or not.
      - 'flag_crisis' : int, 1 or 0 represent *Crisis* available to this character or not.
      - 'goal' : str, short description 
      - 'change' : str, short description 
      - 'crisis' : str, short description
      - 'rule' : str , character rule (Main, Support, Opposites)
      - 'annotation_goal' : str, description  
      - 'annotation_goal' : str, description 
      - 'annotation_goal' : str, description 
      - 'annotation_goal' : str, description 
      - 'annotation_goal' : str, description 
      - 'index' : int, *character_index*. This index is used to get the specify_data in scene[i]['specify_data'][*character_index*]
### scene (list):
  scene list is following the scene index order form 0 to end.
  - scene[i] : dict, scene *i* detail data:
    - 'id': scene id 
    - 'specify_data' : list, detail data for each key character.
      - scene[i]['specify_data'][*character_index*] : dict, key character detail data
        - 'health' : int, Health level
        - 'mental_health' : int, Attitude Toward Goal level
        - 'change' : int, Change level
        - 'crisis' : int, Crisis level
        - 'goal' : int, Goal level
        - 'default_health' : int, default flag  for visulization 
        - 'default_mental_health' : int, default flag  for visulization 
        - 'default_change' : int, default flag  for visulization 
        - 'default_crisis' : int, default flag  for visulization 
        - 'default_goal' : int, default flag  for visulization 
      
      
# Processed Project Data
Get and Save new data: run statistics_collection/get_n_and_path.py \
temporarily only project in USE_PROJECT_ID will be used

data location : statistics_collection/data/movies_data\
You can load data by general/tools.load_data
Each project data is processed and stored in a structure called *Movie* (general/general_class.py)\

Each Key Character has 5 differnet status: health，attitude to goal，change，crisis，goal.\
Each status have 5 levels from 0 to 4. If the value which represents the status level is *9*, it means this status is not avaiable for this character.

## Movie(m_id, m_name, p_id, p_name, characters, main_char)
`parameters`:
 - m_id : int, movie id
 - m_name : str, movie name
 - p_id : int, project id
 - p_name: str, prject name
 - characters :, list, list of key characters information dict as used in original data
 - main_char: dict, movie main character and information as used in original data
 
 `self`:
 - m_id : int, movie id
 - m_name : str, movie name
 - p_id : int, project id
 - p_name: str, prject name
 - characters :, list, list of key characters information dict as used in original data
 - main_char: dict, movie main character and information as used in original data
 - url : corresponding proejct page url link
 - status : ndarray, shape (scene_num, character_num, status_num)
  - cur_status = status[scene_index][character_index][status_index]
  - status order (index) : health(0)，attitude to goal(1)，change(2)，crisis(3)，goal(4)
 - path : ndarray, shape (scene_num-1, character_num)
  - cur_path = path[next_scene_index-1][character_index]
  - cur_path : tuple(str, str), (status_i, status_(i+1)) the path from cur status to next status. e.g. (00000, 11000) 
 
      
# Status and Path Frequency
data location : statistics_collection/data/{n_status, path}\
  
## n_status
status frequency dictionary, key is the status, value is the number of time this status appear in all project.
e.g. : `{"00000" : 14}`

## path
path frequency dictionary, key is the path, value is the number of time this path appear in all project.
e.g. : `{"99940_99900" : 14}`

  
  
