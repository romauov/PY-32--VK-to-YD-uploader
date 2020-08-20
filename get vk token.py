from urllib.parse import urlencode

app_id = 
oauth_url = 'https://oauth.vk.com/authorize'
oauth_data = {
    'client_id': app_id,
    'display': 'page',
    'scope': 'status, audio, friends, photos, video',
    'response_type': 'token',
    'v': 5.12
}

print('?'.join(
    (oauth_url, urlencode(oauth_data))
))