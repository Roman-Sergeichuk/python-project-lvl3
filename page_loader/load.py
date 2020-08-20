import requests
from urllib.parse import urlparse


def make_filename(url):
    parts_url = urlparse(url)
    host_name = parts_url.netloc.replace('.', '-')
    if parts_url.path:
        path = parts_url.path.replace('/', '-')[:-1]
        filename = f'{host_name}{path}'
    else:
        filename = host_name
    return f'{filename}.html'


def load_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response
