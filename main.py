import json
import requests
from tqdm import tqdm
from datetime import date
from pprint import pprint
import configparser


class VkApi():
    def __init__(self, vk_token, vk_ids):
        self.vk_api_url = 'https://api.vk.com/method/'
        self.vk_params = {'access_token': vk_token,
                          'user_ids': vk_ids, 'v': '5.131'}
        self.upload_info = {'info': []}
        self.vk_photo_url = []

    def vk_users_id(self):
        vk_method = self.vk_api_url + 'users.get'
        resp = requests.get(url=vk_method, params=self.vk_params)
        return resp.json()['response'][0]['id']

    def vk_get_photo(self, count=5):
        vk_method, count_likes = self.vk_api_url + 'photos.get', []
        vk_photo_params = {'owner_id': self.vk_users_id(), 'rev': 1,
                           'album_id': 'profile', 'extended': 1}
        resp = requests.get(params=self.vk_params | vk_photo_params,
                            url=vk_method)
        print('Получение ссылок для загрузки.... ')
        for items in resp.json()['response']['items'][0:count]:
            # Определение имени для файла:
            if items['likes']['count'] not in count_likes:
                count_likes.append(items['likes']['count'])
                file_name = f'{items["likes"]["count"]}.jpg'
            else:
                file_name = f'{items["date"]}.jpg'
            # Получение ссылки на фото максимального качества:
            types_list = [i['type'] for i in items['sizes']]
            if 'w' in types_list:
                info = {'file_name': file_name, 'type': 'w'}
                final_url = items['sizes'][types_list.index('w')]['url']
                self.vk_photo_url.append([final_url, file_name])
                self.upload_info['info'].append(info)
            else:
                final_url = items['sizes'][-1]['url']
                info = {'file_name': file_name,
                        'type': items['sizes'][-1]['type']}
                self.vk_photo_url.append([final_url, file_name])
                self.upload_info['info'].append(info)

    def vk_info_json(self):
        with open('reserv_info.json', 'w') as f:
            json.dump(self.upload_info, f)


class YadApi():
    def __init__(self, yad_token):
        self.yad_api_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.yad_headers = {'Authorization': f'OAuth {yad_token}',
                            'Content-Type': 'application/json'}

    def yad_folder_by_date(self):
        params = {"path": f'{str(date.today())}'}
        response = requests.put(headers=self.yad_headers, params=params,
                                url=self.yad_api_url)

    def upload_to_yad(self, content_list):
        print('Загрузка на ЯндексДиск...')
        for items in tqdm(content_list):
            yad_url = self.yad_api_url + '/upload'
            path_to_file = f'{date.today()}/{items[1]}'
            params = {'path': path_to_file, 'url': items[0]}
            responce = requests.post(url=yad_url, params=params,
                                     headers=self.yad_headers)
        print('Готово!')


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('tokens.ini')

    vk_token = config['VK']['token']
    yad_token = config['YaD']['token']

    vk_ids = input('Введите ID или никнейм страницы пользователя VK: ')
    count_photo = int(input('Сколько фотографий Вы хотите загрузить?: '))

    vk_user = VkApi(vk_token=vk_token, vk_ids=vk_ids)
    yad_uploader = YadApi(yad_token=yad_token)

    yad_uploader.yad_folder_by_date()
    vk_user.vk_get_photo(count=count_photo)
    vk_user.vk_info_json()
    yad_uploader.upload_to_yad(vk_user.vk_photo_url)

    print('Информация о загруженных фото сохранена в файл "reserv_info": ')
    with open('reserv_info.json') as f:
        data = json.load(f)
        pprint(data['info'])