import math
import requests
from Node import Node
import os
from tqdm import tqdm
import pickle
from dotenv import load_dotenv
import time

load_dotenv()

session = requests.Session()
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=10))


#Подгружает данные с API Inaturalist
def create_nodes(t_id, nodes):
    res = session.get(BASE_URL + 'taxa' + '?taxon_id=' + str(t_id) + '&locale=RU', headers=headers)
    taxon = res.json()['results'][0]
    parent_id = taxon['parent_id']

    try:
        photo_url = taxon['default_photo']['square_url']
    except:
        photo_url = None
    is_species = False

    if taxon['rank_level'] <= 10:
        is_species = True
        if not os.path.exists(f'photos/{t_id}.png'):
            if photo_url is not None:
                photo = requests.get(photo_url)
                with open(f'photos/{t_id}.png', 'wb') as file:
                    file.write(photo.content)

    try:
        name = taxon['preferred_common_name']
    except:
        name = taxon['name']

    nodes[t_id] = Node(t_id, name, parent_id if t_id != 3 else None, is_species)

    while parent_id not in nodes and t_id != taxon_id:
        create_nodes(parent_id, nodes)


# Сериализация
def save_nodes(nodes, filename=os.getenv("pkl_file_name")):
    with open(filename, "wb") as file:
        pickle.dump(nodes, file)


BASE_URL = 'https://api.inaturalist.org/v1/'
username = 'peterchristiaen' # имя пользователя
taxon_id = 3  # птицы

headers = {'Accept': 'application/json'}
res = requests.get(BASE_URL + 'observations?user_login=' + username + "&taxon_id=" + str(taxon_id), headers=headers)
per_page = res.json()['per_page']
total_observations = res.json()['total_results']

taxs_id = set()

for i in tqdm(range(1, math.ceil(total_observations / per_page) + 1)):
    res_page = requests.get(BASE_URL + 'observations?user_login=' + username + "&taxon_id=" + str(taxon_id) + '&page=' + str(i) + "&locale=RU", headers=headers)
    for item in res_page.json()['results']:
        taxs_id.add(item['taxon']['id'])

nodes = dict()
for t_id in tqdm(taxs_id):
    create_nodes(t_id, nodes)
    time.sleep(1)

save_nodes(nodes)
