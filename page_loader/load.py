import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import os
import sys
from progress.bar import IncrementalBar
from page_loader.log import setup_log


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
    return re.sub(r'(\.|/)', '-', name)


def make_inner_filename(path_to_file):
    parts_url = urlparse(path_to_file)
    path_without_host = parts_url.path
    path = os.path.dirname(path_without_host)
    path = path.replace('/', '-')[1:]
    if path:
        path += '-'
    origin_filename = os.path.basename(path_to_file)
    file_name, extension = os.path.splitext(origin_filename)
    final_filename = ''
    for char in file_name:
        if len(final_filename) >= 50:
            break
        else:
            final_filename += char
    return path + final_filename + extension


def get_response(url, logging_level):
    logger = setup_log(logging_level=logging_level)
    try:
        response = requests.get(url)
    except (requests.exceptions.InvalidSchema,
            requests.exceptions.InvalidURL,
            requests.exceptions.MissingSchema) as e:
        logger.debug(sys.exc_info()[:2])
        logger.error('Ошибка параметров запроса.')
        raise KnownError('Ошибка параметров запроса') from e
    except requests.exceptions.ConnectionError as e:
        logger.debug(sys.exc_info()[:2])
        logger.error(
            'Несуществующий адрес сайта либо ошибка подключения.')
        raise KnownError(
            'Несуществующий адрес сайта либо ошибка подключения.') from e
    if response.status_code in range(400, 500):
        logger.error('Страница не существует.')
        raise KnownError('Страница не существует.')
    elif response.status_code in range(500, 511):
        logger.error('Сервер не отвечает.')
        raise KnownError('Сервер не отвечает.')
    return response


def soup_find_save(url, content_folder, soup, logging_level, tag2find, inner):
    logger = setup_log(logging_level=logging_level)
    session = requests.Session()
    if not os.path.exists(content_folder):  # create only once
        logger.debug('Создание папки с локальным контентом')
        try:
            os.mkdir(content_folder, mode=0o700, dir_fd=None)
        except PermissionError as e:
            logger.debug(sys.exc_info()[:2])
            logger.error('Нет прав на внесение изменений.')
            raise KnownError('Нет прав на внесение изменений.') from e
        except FileNotFoundError as e:
            logger.debug(sys.exc_info()[:2])
            logger.error('Указанный путь не существует.')
            raise KnownError('Указанный путь не существует.') from e
        logger.debug('Папка с локальным контентом успешно создана')
    resources = soup.findAll(tag2find)
    files_count = len(resources)
    content_name = ''
    if tag2find == 'img':
        content_name = 'images'
    if tag2find == 'link':
        content_name = 'links'
    if tag2find == 'script':
        content_name = 'scripts'
    bar = IncrementalBar(f'Loading {content_name}:', max=files_count)
    for res in soup.findAll(tag2find):
        if not res.has_attr(inner):
            logger.info(f'Отсутствует атрибут {inner}. Нечего скачивать')
            bar.next()
            continue
        inner_file_name = make_inner_filename(res[inner])
        fileurl = urljoin(url, res.get(inner))
        filepath = os.path.join(content_folder, inner_file_name)
        # rename html ref so can move html and folder of files anywhere
        content_dir_name = os.path.basename(content_folder)
        res[inner] = os.path.join(content_dir_name, inner_file_name)
        logger.debug(inner_file_name)
        try:
            if not os.path.isfile(filepath):  # was not downloaded
                with open(filepath, 'wb') as file:
                    filebin = session.get(fileurl)
                    file.write(filebin.content)
        except Exception:
            logger.warning('Нет прав на внесение изменений', exc_info=True)
            print('Не удалось загрузить файл')
        bar.next()
    bar.finish()
    return soup


def save_page(url, output, logging_level):
    logger = setup_log(logging_level=logging_level)
    logger.debug('Старт загрузки')
    response = get_response(url, logging_level)
    soup = BeautifulSoup(response.text, features="lxml")
    page_folder_name = make_page_name(url) + '_files'
    folder_path = os.path.join(output, page_folder_name)
    logger.info('Поиск и загрузка картинок')
    soup = soup_find_save(url, folder_path, soup,
                          logging_level, tag2find='img', inner='src')
    logger.info('Поиск и загрузка ссылок')
    soup = soup_find_save(url, folder_path, soup,
                          logging_level, tag2find='link', inner='href')
    logger.info('Загрузка скриптов')
    soup = soup_find_save(url, folder_path, soup,
                          logging_level, tag2find='script', inner='src')
    page_name = make_page_name(url) + '.html'
    path_to_file = os.path.join(output, page_name)
    logger.debug(path_to_file)
    try:
        with open(path_to_file, 'wb') as file:
            file.write(soup.prettify('utf-8'))
    except PermissionError as e:
        logger.error('Нет прав на внесение изменений', exc_info=True)
        raise KnownError('Нет прав на внесение изменений') from e
    else:
        logger.info('Страница успешно загружена')
    return path_to_file, page_folder_name
