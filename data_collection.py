import math
import requests
import os
import pickle
import time
from tqdm import tqdm

from Node import Node

# Создаем сессию для выполнения HTTP-запросов
session = requests.Session()
session.mount("https://", requests.adapters.HTTPAdapter(max_retries=10))

BASE_URL = 'https://api.inaturalist.org/v1/'
username = 'merrcurys'  # Имя пользователя для запроса наблюдений
taxon_id = 3  # ID таксона (в данном случае - птицы)
headers = {'Accept': 'application/json'}


def create_nodes(t_id, nodes):
    """Рекурсивно создает узлы таксонов и их родителей, загружает фото"""
    # Получаем информацию о таксоне по его ID
    res = session.get(
        f"{BASE_URL}taxa?taxon_id={t_id}&locale=RU",
        headers=headers,
        timeout=600
    )

    if res.status_code == 429:  # >100 запросов в минуту
        print(f"\nПревышен лимит запросов в минуту на одного пользователя. Подождем минуту и продолжим.")
        time.sleep(60)
        return create_nodes(t_id, nodes)

    taxon = res.json()['results'][0]
    parent_id = taxon['parent_id']
    photo_url = taxon.get('default_photo', {}).get('square_url')

    # Загрузка фото
    if taxon['rank_level'] <= 10 and photo_url:
        photo_path = os.path.abspath(f'input/photos/{t_id}.png')
        if not os.path.exists(photo_path):
            try:
                photo = requests.get(photo_url, timeout=600)

                if photo.status_code == 429:  # >100 запросов в минуту
                    print(f"\nПревышен лимит запросов в минуту на одного пользователя. Подождем минуту и продолжим.")
                    time.sleep(60)
                    return create_nodes(t_id, nodes)

                if photo.status_code == 200:
                    with open(photo_path, 'wb') as f:
                        f.write(photo.content)

            except Exception as e:
                print(f"Ошибка при загрузке фото {t_id}: {e}")

    # Получаем имя таксона, либо его предпочитаемое общее название
    name = taxon.get('preferred_common_name', taxon['name'])
    # Создаем узел для таксона и добавляем его в словарь
    nodes[t_id] = Node(t_id, name, parent_id, taxon['rank_level'] <= 10)

    # Рекурсия для родителя, если он существует и еще не обработан
    if parent_id is not None and parent_id not in nodes:
        create_nodes(parent_id, nodes)


def save_nodes(nodes, filename="input/nodes.pkl"):
    """Сохраняет узлы в файл"""
    with open(filename, "wb") as file:
        pickle.dump(nodes, file)


def fetch_observations():
    """Возвращает общее число наблюдений и количество на странице"""
    res = requests.get(f"{BASE_URL}observations", params={
                       'user_login': username, 'taxon_id': taxon_id}, headers=headers)
    total_observations = res.json()['total_results']
    per_page = res.json()['per_page']
    return total_observations, per_page


def main():
    """Основная логика: сбор данных наблюдений, создание узлов таксонов, сохранение"""
    # Создаем папку для сохранения фотографий, если она не существует
    os.makedirs('input/photos', exist_ok=True)

    # Получаем общее количество наблюдений и количество на странице
    total_observations, per_page = fetch_observations()
    taxs_id = set()  # Множество для хранения уникальных ID таксонов

    # Запрашиваем данные по страницам
    for i in tqdm(range(1, math.ceil(total_observations / per_page) + 1)):
        res_page = requests.get(f"{BASE_URL}observations", params={
                                'user_login': username, 'taxon_id': taxon_id, 'page': i, 'locale': 'RU'}, headers=headers)
        # Обновляем множество уникальных таксонов
        taxs_id.update(item['taxon']['id']
                       for item in res_page.json()['results'])

    nodes = {}  # Словарь для хранения узлов
    for t_id in tqdm(taxs_id):
        create_nodes(t_id, nodes)  # Создаем узлы для каждого таксона

    save_nodes(nodes)
    print(f"Сохранено {len(nodes)} узлов в файл nodes.pkl")


if __name__ == "__main__":
    main()
