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


def create_nodes(t_id, nodes):
    res = session.get(BASE_URL + 'taxa' + '?taxon_id=' +
                      str(t_id) + '&locale=RU', headers=headers)
    taxon = res.json()['results'][0]
    parent_id = taxon['parent_id']

    try:
        photo_url = taxon['default_photo']['square_url']
    except:
        photo_url = None

    is_species = taxon['rank_level'] <= 10

    # Создание папки для фото
    if not os.path.exists('photos'):
        os.makedirs('photos')

    # Загрузка фото для видов
    if is_species and photo_url:
        photo_path = os.path.abspath(f'photos/{t_id}.png')
        if not os.path.exists(photo_path):
            try:
                photo = requests.get(photo_url, timeout=10)
                if photo.status_code == 200:
                    with open(photo_path, 'wb') as file:
                        file.write(photo.content)
                else:
                    print(f"Ошибка загрузки фото {t_id}: {photo.status_code}")
            except Exception as e:
                print(f"Ошибка при загрузке фото {t_id}: {str(e)}")

    # Получение названия
    name = taxon.get('preferred_common_name', taxon['name'])

    nodes[t_id] = Node(t_id, name, parent_id if t_id !=
                       3 else None, is_species)

    # Рекурсивное создание родительских узлов
    while parent_id not in nodes and t_id != taxon_id:
        create_nodes(parent_id, nodes)


def save_nodes(nodes, filename=None):
    filename = filename or os.getenv("pkl_file_name", "nodes.pkl")
    with open(filename, "wb") as file:
        pickle.dump(nodes, file)


if __name__ == '__main__':
    BASE_URL = 'https://api.inaturalist.org/v1/'
    username = 'merrcurys'
    taxon_id = 3  # Птицы
    headers = {'Accept': 'application/json'}

    # Получение списка наблюдений
    res = requests.get(BASE_URL + 'observations',
                       params={'user_login': username, 'taxon_id': taxon_id},
                       headers=headers)

    total_observations = res.json()['total_results']
    per_page = res.json()['per_page']
    taxs_id = set()

    # Сбор ID таксонов
    for i in tqdm(range(1, math.ceil(total_observations / per_page) + 1)):
        res_page = requests.get(BASE_URL + 'observations',
                                params={
                                    'user_login': username,
                                    'taxon_id': taxon_id,
                                    'page': i,
                                    'locale': 'RU'
                                },
                                headers=headers)
        for item in res_page.json()['results']:
            taxs_id.add(item['taxon']['id'])

    # Создание узлов
    nodes = dict()
    for t_id in tqdm(taxs_id):
        create_nodes(t_id, nodes)
        time.sleep(1)  # Ограничение запросов

    save_nodes(nodes)
    print(
        f"Сохранено {len(nodes)} узлов в файл {os.getenv('pkl_file_name', 'nodes.pkl')}")
