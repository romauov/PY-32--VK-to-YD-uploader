import requests
from pprint import pprint
import time
from tokens import vk_token, yd_token


target_id = ''


def vk_backup(target_id, vk_token, yd_token):

    if type(target_id) == str:

        try:
            r = requests.get(
                'https://api.vk.com/method/users.get',
                params={
                    'access_token': vk_token,
                    'v': 5.89,
                    'user_ids': target_id,

                }
            )
            target_id = r.json()['response'][0]['id']

        except:
            r = requests.get(
                'https://api.vk.com/method/groups.getById',
                params={
                    'access_token': vk_token,
                    'v': 5.61,
                    'group_ids': target_id,

                }
            )
            target_id = r.json()['response'][0]['id'] * (-1)

    if target_id > 0:
        user_name, folder_name = user_info_request(target_id, vk_token)
    else:
        user_name, folder_name = group_info_request(target_id, vk_token)


    create_YD_folder(yd_token, folder_name)
    album_ids = get_albums_list(target_id, vk_token)
    albums_count = len(album_ids)
    j = 1
    for album_id in album_ids:
        urls = user_photos_request(target_id, vk_token, album_id)
        photos_count = len(urls)

        photo_uploader(yd_token, urls, folder_name, photos_count, albums_count, j)
        j += 1

    print('загрузка файлов завершена')

    return


def user_info_request(target_id, vk_token):

    user_info = requests.get(
                'https://api.vk.com/method/users.get',
                params={
                    'access_token' : vk_token,
                    'v' : 5.89,
                    'user_ids' : target_id,

                }
            )

    user_name = user_info.json()['response'][0]['first_name'] + ' ' + user_info.json()['response'][0]['last_name']

    folder_name = 'VK backup ' + user_name + ' ' + str(target_id)

    print('получены данные о пользователе')

    return user_name, folder_name

def group_info_request(target_id, vk_token):

    group_info = requests.get(
                'https://api.vk.com/method/groups.getById',
                params={
                    'access_token' : vk_token,
                    'v' : 5.61,
                    'group_ids' : abs(target_id),

                }
            )

    user_name = group_info.json()['response'][0]['screen_name']
    folder_name = 'VK backup ' + user_name + ' ' + str(abs(target_id))

    print('получены данные о группе')

    return user_name, folder_name

def grab_urls_for_back_up(user_photos, urls_for_back_up):

    photos = user_photos.json()['response']['items']

    for photo in photos:
        
        photo_sizes = photo['sizes']
        
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
    print('собраны ссылки для загрузки фотографий')

def get_albums_list(target_id, vk_token):
    albums = requests.get(
        'https://api.vk.com/method/photos.getAlbums',
        params={
            'access_token': vk_token,
            'v': 5.124,
            'owner_id': target_id
        }
    )
    albums = albums.json()['response']['items']
    album_ids = [album['id'] for album in albums]
    album_ids.append('wall')
    album_ids.append('profile')

    return album_ids

def user_photos_request(target_id, vk_token, album_id):
    user_photos = requests.get(
        'https://api.vk.com/method/photos.get',
        params={
            'access_token': vk_token,
            'v': 5.77,
            'owner_id': target_id,
            'album_id': album_id,
            'count': 200,
            'extended': 1,
            # 'no_service_albums': 1
        }
    )

    urls_for_back_up = []

    back_up_iterations = user_photos.json()['response']['count'] // 200 + 1

    for iteration in range(back_up_iterations):
        user_photos = requests.get(
            'https://api.vk.com/method/photos.get',
            params={
                'access_token': vk_token,
                'v': 5.77,
                'owner_id': target_id,
                'album_id': album_id,
                'count': 200,
                'offset': iteration * 200,
                'extended': 1
            }
        )

        grab_urls_for_back_up(user_photos, urls_for_back_up)

    print('получена информация о фотографиях')

    return urls_for_back_up

def create_YD_folder(yd_token, folder_name):

    auth = {'Authorization': f'OAuth {yd_token}'}
    create_folder = requests.put(f'https://cloud-api.yandex.net/v1/disk/resources?path=disk%3A%2F{folder_name}',
                            headers=auth)
    print('создана папка на я.диске')

def photo_uploader(YD_token, urls_for_back_up, folder_name, photos_count, albums_count, j):
    i = 1

    for url in urls_for_back_up:

        upload_url = url['url']
        file_name = url['pic_name']

        url_upload(YD_token, upload_url, file_name, folder_name)

        pprint(f'загружено фото {i} из {photos_count} \\ альбом {j} из {albums_count}')

        i += 1

    return

def url_upload(yd_token, upload_url, file_name, folder_name):
    auth = {'Authorization': f'OAuth {yd_token}'}

    upload_photo = requests.post(
        f'https://cloud-api.yandex.net:443/v1/disk/resources/upload?path={folder_name}%2F{file_name}&url={upload_url}',
        headers=auth)


    if 'error' in upload_photo.json().keys():
        pprint('ошибка при отправки файла. повторная попытка через 5 сек.')
        pprint(upload_photo.json())

        time.sleep(5)
        return url_upload(yd_token, upload_url, file_name, folder_name)

if __name__ == '__main__':

    vk_backup(target_id, vk_token, yd_token)






















