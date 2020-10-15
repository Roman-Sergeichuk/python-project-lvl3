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
SOURCE = {LINK: HREF, SCRIPT: SRC, IMG: SRC}
TEXT, BIN = 'text', 'bin'
PATH_LENGTH_LIMIT = 255


class KnownError(Exception):  # pragma: no cover
    pass


def make_page_name(url):
    parts_url = urlparse(url)
    host_name = parts_url.netloc
    if parts_url.path:
        path = parts_url.path
        name = f'{host_name}{path}'
    else:
        name = host_name
    return re.sub(r'[^0-9a-zA-Z]', '-', name)


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
        logging.debug(traceback.format_exc(10))
        logging.error('Ошибка параметров запроса')
        raise KnownError('Ошибка параметров запроса') from e
    except requests.exceptions.ConnectionError as e:
        logging.debug(traceback.format_exc(10))
        logging.error(
            'Несуществующий адрес сайта либо ошибка подключения')
        raise KnownError(
            'Несуществующий адрес сайта либо ошибка подключения') from e
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in range(400, 500):
            logging.debug(traceback.format_exc(10))
            logging.error('Страница не существует')
            raise KnownError('Страница не существует')
        elif e.response.status_code in range(500, 511):
            logging.debug(traceback.format_exc(10))
            logging.error('Сервер не отвечает')
            raise KnownError('Сервер не отвечает')
    return response.text


def create_dir(path_to_dir):
    if not os.path.exists(path_to_dir):
        logging.debug('Создание папки с локальным контентом')
        try:
            os.mkdir(path_to_dir, mode=0o700, dir_fd=None)
        except PermissionError as e:
            logging.debug(traceback.format_exc(10))
            logging.error('Нет прав на внесение изменений.')
            raise KnownError('Нет прав на внесение изменений.') from e
        except FileNotFoundError as e:
            logging.debug(traceback.format_exc(10))
            logging.error('Указанный путь не существует.')
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
    for tag_name, attribute in SOURCE.items():
        resources_by_one_tag = resources_find_rename(
            url, content_folder_path, soup,
            tag2find=tag_name, inner=attribute)
        all_resources += resources_by_one_tag
    return all_resources


def save_to_file(full_file_name, content, format):
    write_mode = "w" if format == TEXT else 'wb'
    logging.info("Сохраняем файл {}".format(full_file_name))
    try:
        with open(full_file_name, write_mode) as output_file:
            output_file.write(content)
    except IOError:
        logging.debug(traceback.format_exc(10))
        logging.error("Не удалось сохранить файл {}".format(full_file_name))


def load_local_content(resources):
    bar = IncrementalBar('Загрузка страницы:', max=len(resources))
    for resource in resources:
        fileurl, filepath = resource
        if os.path.isfile(filepath):
            filename, extension = os.path.splitext(filepath)
            filename += '_'
            filepath = filename + extension
        session = requests.Session()
        try:
            local = session.get(fileurl)
        except requests.exceptions.InvalidSchema:
            logging.debug(traceback.format_exc(10))
            continue
        if 'css' in local.headers['content-type'] or \
                'javascript' in local.headers['content-type']:
            save_to_file(filepath, local.text, TEXT)
            bar.next()
        else:
            save_to_file(filepath, local.content, BIN)
            bar.next()
    bar.finish()


def save_page(url, output):
    logging.debug('Старт загрузки')
    response = get_response(url)
    content_folder_name = make_page_name(url) + '_files'
    content_folder_path = os.path.join(output, content_folder_name)
    soup = BeautifulSoup(response, features="lxml")
    resources = collect_all_resources(url, content_folder_path, soup)
    page_name = make_page_name(url) + '.html'
    path_to_file = os.path.join(output, page_name)
    save_to_file(path_to_file, soup.prettify('utf-8'), BIN)
    create_dir(content_folder_path)
    load_local_content(resources)
    logging.debug('Загрузка завершена')
    return path_to_file, content_folder_name
