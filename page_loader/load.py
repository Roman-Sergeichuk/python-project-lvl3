import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import os
import sys


# def page_name(url):
#     parts_url = urlparse(url)
#     host_name = parts_url.netloc.replace('.', '-')
#     if parts_url.path:
#         path = parts_url.path.replace('/', '-')
#         name = re.sub('^(\.|-)$', '', f'{host_name}{path}')
#     else:
#         name = host_name
#     return name


def make_page_name(url):
    parts_url = urlparse(url)
    host_name = parts_url.netloc
    if parts_url.path:
        path = parts_url.path
        name = f'{host_name}{path}'
    else:
        name = host_name
    return re.sub(r'(\.|/)', '-', name)


def make_inner_filename(path_to_file):
    parts_url = urlparse(path_to_file)
    path_without_host = parts_url.path
    path = os.path.dirname(path_without_host)
    path = path.replace('/', '-')[1:]
    origin_filename = os.path.basename(path_to_file)
    file_name, extension = os.path.splitext(origin_filename)
    final_filename = ''
    for char in file_name:
        final_filename += char
        if len(final_filename) >= 40:
            final_filename = path + final_filename + extension
            break
    else:
        final_filename = path + final_filename + extension
    return final_filename


def get_response(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response


def save_page(url, output):
    def soup_find_save(pagefolder, tag2find='img', inner='src'):
        """saves on specified `pagefolder` all tag2find objects"""
        if not os.path.exists(pagefolder):  # create only once
            os.mkdir(pagefolder)
        for res in soup.findAll(tag2find):  # images, css, etc..
            try:
                if not res.has_attr(inner):
                    continue  # may or may not exist
                inner_filename = make_inner_filename(res[inner])
                fileurl = urljoin(url, res.get(inner))
                filepath = os.path.join(pagefolder, inner_filename)
                # rename html ref so can move html and folder of files anywhere
                res[inner] = os.path.join(os.path.basename(pagefolder), inner_filename)  # noqa: E501
                if not os.path.isfile(filepath):  # was not downloaded
                    with open(filepath, 'wb') as file:
                        filebin = session.get(fileurl)
                        file.write(filebin.content)
            except Exception as exc:
                print(exc, file=sys.stderr)
        return soup

    session = requests.Session()
    # ... whatever other requests config you need here
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features="lxml")
    page_folder_name = make_page_name(url) + '_files'
    folder_path = os.path.join(output, page_folder_name)
    soup = soup_find_save(folder_path, 'img', 'src')
    soup = soup_find_save(folder_path, 'link', 'href')
    soup = soup_find_save(folder_path, 'script', 'src')
    page_name = make_page_name(url) + '.html'
    path_to_file = os.path.join(output, page_name)
    with open(path_to_file, 'wb') as file:
        file.write(soup.prettify('utf-8'))
    return path_to_file, page_folder_name
