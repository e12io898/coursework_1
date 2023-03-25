import requests
import json
from datetime import *
from tqdm import tqdm
from pprint import pprint

def token_get():
    """ Функция считывает токен VK из файла VKtoken.txt """
    with open('VKtoken.txt', 'r') as file_object:
        token = file_object.read()
        return token

class VkToYaDisk():
    """ Класс для выгрузки фотографий профиля VK на ЯндексДиск """
    def __init__(self,
                 vk_token=token_get(),
                 vk_ids=int(input('Введите ID пользователя VK: ')),
                 ya_token=input('Введите токен Яндекса: ')):
        self.yad_headers = {'Content-Type': 'application/json',
                            'Authorization': f'OAuth {ya_token}'}
        self.yad_api_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.vk_params = {'access_token': vk_token,
                          'album_id': 'profile',
                          'owner_id': vk_ids,
                          'extended': 1,
                          'v': '5.131',
                          'rev': 1}
        self.upload_info = {"info": ''}

    def yandex_folder(self):
        """" Функция создаёт папку на ЯндексДиске с именем по текущей дате """
        params = {"path": f'{str(date.today())}'}
        response = requests.put(self.yad_api_url,
                                headers=self.yad_headers,
                                params=params)

    def post_to_yad(self, params):
        """ Функция загрузки фото на ЯндексДиск """
        response = requests.post(self.yad_api_url + '/upload',
                                 headers=self.yad_headers,
                                 params=params)

    def yad_upload(self, count=5):
        """ Метод получает ссылки на фотографии профиля VK и выгружает
            их на ЯндексДиск в папку с именем по текущей дате;
            информация о загруженных фото сохраняется в json файл"""
        count_likes, vk_url = [], 'https://api.vk.com/method/photos.get'
        self.yandex_folder()
        resp = requests.get(vk_url, params=self.vk_params)
        info_list = []
        for items in tqdm(resp.json()['response']['items'][0:count]):
            # выбор имени для конечного файла на ЯндексДиске:
            if items['likes']['count'] not in count_likes:
                count_likes.append(items['likes']['count'])
                file_name = items["likes"]["count"]
            else:
                file_name = items["date"]
            # список типов качества фото:
            types_list = []
            for type_quality in items['sizes']:
                types_list.append(type_quality['type'])
            # выбор максимального качества и загрузка на ЯндексДиск:
            if 'w' in types_list:
                final_url = items['sizes'][types_list.index('w')]['url']
                path_to_file = f'{date.today()}/{file_name}.jpg'
                params = {'path': path_to_file, 'url': final_url}
                self.post_to_yad(params)
                info_list.append({'file_name': f'{file_name}.jpg',
                                  'type': 'w'})
            else:
                final_url = items['sizes'][-1]['url']
                path_to_file = f'{date.today()}/{file_name}.jpg'
                params = {'path': path_to_file, 'url': final_url}
                self.post_to_yad(params)
                info_list.append({'file_name': f'{file_name}.jpg',
                                  'type': items['sizes'][-1]['type']})
            self.upload_info["info"] = info_list
        with open('reserv_info.json', 'w') as f:
            json.dump(self.upload_info, f)
        print('Фотографии профиля загружены!')


if __name__ == "__main__":
    test = VkToYaDisk()
    test.yad_upload(10)
    print()
    with open('reserv_info.json') as f:
        data = json.load(f)
        pprint(data['info'])