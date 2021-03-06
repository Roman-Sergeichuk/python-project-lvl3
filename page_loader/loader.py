import logging
import os
import re
import traceback
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar


LINK, SCRIPT, IMG = 'link', 'script', 'img'
SRC, HREF = 'src', 'href'
SOURCE = (LINK, HREF), (SCRIPT, SRC), (IMG, SRC)
FILES, HTML = '_files', '.html'
PATH_LENGTH_LIMIT = 50
MIME_TYPE = 'content-type'
MIME_SUBTYPES = 'text/css', 'text/javascript'


class KnownError(Exception):  # pragma: no cover
    pass


def make_page_name(url, ending):
    parts_url = urlparse(url)
    host_name = parts_url.netloc
    if parts_url.path:
        path = parts_url.path
        name = f'{host_name}{path}'
    else:
        name = host_name
    return f'{re.sub(r"[^0-9a-zA-Z]", "-", name)}{ending}'


def make_inner_filename(url):
    parts_url = urlparse(url)
    path_without_host = parts_url.path
    path = os.path.dirname(path_without_host)
    path = path.replace('/', '-')[1:]
    if path:
        path += '-'
    origin_filename = os.path.basename(url)
    file_name, extension = os.path.splitext(origin_filename)
    path = re.sub(r'[^0-9a-zA-Z]+', '-', path)
    file_name = re.sub(r'[^0-9a-zA-Z]+', '_', file_name)
    # Иногда к расширениям прицепляются query strings:
    extension = (extension.split('?'))[0]
    final_filename = (path + file_name)[:PATH_LENGTH_LIMIT]
    return final_filename + extension


def get_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except (requests.exceptions.InvalidSchema,
            requests.exceptions.InvalidURL,
            requests.exceptions.MissingSchema) as e:
        raise KnownError('Ошибка параметров запроса') from e
    except requests.exceptions.ConnectionError as e:
        raise KnownError(
            'Несуществующий адрес сайта либо ошибка подключения') from e
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in range(400, 500):
            raise KnownError('Страница не существует') from e
        elif e.response.status_code in range(500, 511):
            raise KnownError('Сервер не отвечает') from e
    return response


def create_dir(path_to_dir):
    if not os.path.exists(path_to_dir):
        logging.debug('Создание папки с локальным контентом')
        try:
            os.mkdir(path_to_dir, mode=0o700, dir_fd=None)
        except PermissionError as e:
            raise KnownError('Нет прав на внесение изменений.') from e
        except FileNotFoundError as e:
            raise KnownError('Указанный путь не существует.') from e
        logging.debug('Папка с локальным контентом успешно создана')


def resources_find_rename(url, content_folder, soup, tag2find, inner):
    resources_by_one_tag = []
    for res in soup.findAll(tag2find):
        if not res.has_attr(inner):
            continue
        inner_file_name = make_inner_filename(res[inner])
        logging.debug(res[inner])
        fileurl = urljoin(url, res.get(inner))
        filepath = os.path.join(content_folder, inner_file_name)
        content_dir_name = os.path.basename(content_folder)
        res[inner] = os.path.join(content_dir_name, inner_file_name)
        resources_by_one_tag.append((fileurl, filepath))
    return resources_by_one_tag


def collect_all_resources(url, content_folder_path, soup):
    all_resources = []
    for tag_name, attribute in SOURCE:
        resources_by_one_tag = resources_find_rename(
            url, content_folder_path, soup,
            tag2find=tag_name, inner=attribute)
        all_resources += resources_by_one_tag
    return all_resources


def save_to_file(full_file_name, content):
    if type(content) == str:
        write_mode = "w"
    elif type(content) == bytes:
        write_mode = 'wb'
    else:
        raise TypeError('Неизвестный тип контента')
    logging.info("Сохраняем файл {}".format(full_file_name))
    try:
        with open(full_file_name, write_mode) as output_file:
            output_file.write(content)
    except IOError:
        logging.debug(traceback.format_exc(10))
        logging.error("Не удалось сохранить файл {}".format(full_file_name))


def load_local_content(resource):
    fileurl, filepath = resource
    if os.path.isfile(filepath) or os.path.isdir(filepath):
        filename, extension = os.path.splitext(filepath)
        filename += '_'
        filepath = filename + extension
    session = requests.Session()
    try:
        local = session.get(fileurl)
    except requests.exceptions.InvalidSchema:
        logging.debug(traceback.format_exc(10))
    else:
        if local.headers[MIME_TYPE] in MIME_SUBTYPES:
            save_to_file(filepath, local.text)
        else:
            save_to_file(filepath, local.content)


def save_page(url, output):
    response = get_response(url)
    soup = BeautifulSoup(response.text, features="lxml")
    content_folder_name = make_page_name(url, FILES)
    content_folder_path = os.path.join(output, content_folder_name)
    resources = collect_all_resources(url, content_folder_path, soup)
    page_name = make_page_name(url, HTML)
    path_to_file = os.path.join(output, page_name)
    save_to_file(path_to_file, soup.prettify('utf-8'))
    create_dir(content_folder_path)
    with IncrementalBar('Загрузка ресурсов:', max=len(resources)) as bar:
        for resource in resources:
            load_local_content(resource)
            bar.next()
    logging.debug('Загрузка завершена')
    return path_to_file, content_folder_name
