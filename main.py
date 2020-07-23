import requests
from pprint import pprint
import time

VK_token = ' '
YD_token = ' '

target_id = ''


def VK_backup(target_id, VK_token, YD_token):

    if target_id > 0:
        user_name, folder_name = user_info_request(target_id, VK_token)
    else:
        user_name, folder_name = group_info_request(target_id, VK_token)


    create_YD_folder(YD_token, folder_name)

    urls = user_photos_request(target_id, VK_token)
    photos_count = len(urls)

    photo_uploader(YD_token, urls, folder_name, photos_count)

    pprint('загрузка файлов завершена')

    return


def user_info_request(target_id, VK_token):

    user_info = requests.get(
                'https://api.vk.com/method/users.get',
                params={
                    'access_token' : VK_token,
                    'v' : 5.89,
                    'user_ids' : target_id,

                }
            )

    user_name = user_info.json()['response'][0]['first_name'] + ' ' + user_info.json()['response'][0]['last_name']
    folder_name = 'VK backup ' + user_name + ' ' + str(target_id)

    return user_name, folder_name

def group_info_request(target_id, VK_token):

    group_info = requests.get(
                'https://api.vk.com/method/groups.getById',
                params={
                    'access_token' : VK_token,
                    'v' : 5.61,
                    'group_ids' : abs(target_id),

                }
            )

    user_name = group_info.json()['response'][0]['screen_name']
    folder_name = 'VK backup ' + user_name + ' ' + str(abs(target_id))

    return user_name, folder_name

def grab_urls_for_back_up(user_photos, urls_for_back_up):

    photos = user_photos.json()['response']['items']

    for photo in photos:
        photo_sizes = photo['sizes']
        # pprint('===================')
        # pprint(photo_sizes)
        pic_name = str(time.ctime(photo['date'])) + ' likes ' + str(photo['likes']['count'])  #str(photo['text'])
        pic_name = pic_name.replace(' ', '_')
        pic_name = pic_name.replace(':', '-')

        for size in photo_sizes:
            # pprint(size)
            if size['type'] == 'w':
                url_dict = {'url' : size['url'], 'pic_name' : pic_name}
                urls_for_back_up.append(url_dict)
                break
            elif size['type'] == 'z':
                url_dict = {'url' : size['url'], 'pic_name' : pic_name}
                urls_for_back_up.append(url_dict)
                break
            elif size['type'] == 'y':
                url_dict = {'url' : size['url'], 'pic_name' : pic_name}
                urls_for_back_up.append(url_dict)
                break


def user_photos_request(target_id, VK_token):
    user_photos = requests.get(
        'https://api.vk.com/method/photos.getAll',
        params={
            'access_token': VK_token,
            'v': 5.77,
            'owner_id': target_id,
            'count': 200,
            'extended': 1,
            # 'no_service_albums': 1
        }
    )

    photos = user_photos.json()['response']['items']

    urls_for_back_up = []

    back_up_iterations = user_photos.json()['response']['count'] // 200 + 1



    for iteration in range(back_up_iterations):
        user_photos = requests.get(
            'https://api.vk.com/method/photos.getAll',
            params={
                'access_token': VK_token,
                'v': 5.77,
                'owner_id': target_id,
                'count': 200,
                'offset': iteration * 200,
                'extended': 1
            }
        )

        grab_urls_for_back_up(user_photos, urls_for_back_up)
    # pprint(urls_for_back_up)
    # pprint(len(urls_for_back_up))

    return urls_for_back_up

def create_YD_folder(YD_token, folder_name):

    auth = {'Authorization': f'OAuth {YD_token}'}
    create_folder = requests.put(f'https://cloud-api.yandex.net/v1/disk/resources?path=disk%3A%2F{folder_name}',
                            headers=auth)

def photo_uploader(YD_token, urls_for_back_up, folder_name, photos_count):
    i = 1

    for url in urls_for_back_up:

        # if i == 5:
        #     return

        upload_url = url['url']
        file_name = url['pic_name']

        url_upload(YD_token, upload_url, file_name, folder_name)

        pprint(f'загружено фото {i} из {photos_count}')
        # pprint(upload_photo.json()['error'])

        i += 1

    return

def url_upload(YD_token, upload_url, file_name, folder_name):
    auth = {'Authorization': f'OAuth {YD_token}'}

    upload_photo = requests.post(
        f'https://cloud-api.yandex.net:443/v1/disk/resources/upload?path={folder_name}%2F{file_name}&url={upload_url}',
        headers=auth)


    if 'error' in upload_photo.json().keys():
        pprint('ошибка при отправки файла. повторная попытка через 5 сек.')
        pprint(upload_photo.json())

        time.sleep(5)
        return url_upload(YD_token, upload_url, file_name, folder_name)

VK_backup(target_id, VK_token, YD_token)






















