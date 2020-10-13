import os
import re
import sys
import traceback
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from progress.bar import IncrementalBar

from page_loader import logging

OBLIGATORY, OPTIONAL = 'obligatory', 'optional'
LINK, SCRIPT, IMG = 'link', 'script', 'img'
SRC, HREF = 'src', 'href'
SOURCE = {LINK: HREF, SCRIPT: SRC, IMG: SRC}
TEXT, BIN = 'text', 'bin'


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


def make_inner_filename(url):
    parts_url = urlparse(url)
    path_without_host = parts_url.path
    path = os.path.dirname(path_without_host)
    path = path.replace('/', '-')[1:]
    if path:
        path += '-'
    origin_filename = os.path.basename(url)
    file_name, extension = os.path.splitext(origin_filename)
    final_filename = ''
    for char in file_name:
        if len(final_filename) >= 50:
            break
        else:
            final_filename += char
    return path + final_filename + extension


def get_response(url, logging_level):
    logger = logging.setup(logging_level=logging_level)
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
    return response.content


def create_dir(path_to_dir):
    if not os.path.exists(path_to_dir):  # create only once
        # logger.debug('Создание папки с локальным контентом')
        try:
            os.mkdir(path_to_dir, mode=0o700, dir_fd=None)
        except PermissionError as e:
            # logger.debug(sys.exc_info()[:2])
            # logger.error('Нет прав на внесение изменений.')
            raise KnownError('Нет прав на внесение изменений.') from e
        except FileNotFoundError as e:
            # logger.debug(sys.exc_info()[:2])
            # logger.error('Указанный путь не существует.')
            raise KnownError('Указанный путь не существует.') from e
        # logger.debug('Папка с локальным контентом успешно создана')


def soup_find_save(url, content_folder, soup, logging_level, tag2find, inner):
    logger = logging.setup(logging_level=logging_level)
    session = requests.Session()
    # if not os.path.exists(content_folder):  # create only once
    #     logger.debug('Создание папки с локальным контентом')
    #     try:
    #         os.mkdir(content_folder, mode=0o700, dir_fd=None)
    #     except PermissionError as e:
    #         logger.debug(sys.exc_info()[:2])
    #         logger.error('Нет прав на внесение изменений.')
    #         raise KnownError('Нет прав на внесение изменений.') from e
    #     except FileNotFoundError as e:
    #         logger.debug(sys.exc_info()[:2])
    #         logger.error('Указанный путь не существует.')
    #         raise KnownError('Указанный путь не существует.') from e
    #     logger.debug('Папка с локальным контентом успешно создана')
    # resources = soup.findAll(tag2find)
    # files_count = len(resources)
    # content_name = ''
    # if tag2find == 'img':
    #     content_name = 'images'
    # if tag2find == 'link':
    #     content_name = 'links'
    # if tag2find == 'script':
    #     content_name = 'scripts'
    # bar = IncrementalBar(f'Loading {content_name}:', max=files_count)
    resources = []
    for res in soup.findAll(tag2find):
        if not res.has_attr(inner):
            logger.info(f'Отсутствует атрибут {inner}. Нечего скачивать')
            # bar.next()
            continue
        inner_file_name = make_inner_filename(res[inner])
        fileurl = urljoin(url, res.get(inner))
        filepath = os.path.join(content_folder, inner_file_name)
        # rename html ref so can move html and folder of files anywhere
        content_dir_name = os.path.basename(content_folder)
        res[inner] = os.path.join(content_dir_name, inner_file_name)
        resources.append((fileurl, filepath))
        # print((fileurl, filepath))
        logger.debug(inner_file_name)
        # try:
        #     if not os.path.isfile(filepath):  # was not downloaded
        #         with open(filepath, 'wb') as file:
        #             filebin = session.get(fileurl)
        #             file.write(filebin.content)
        # except Exception:
        #     logger.warning('Нет прав на внесение изменений', exc_info=True)
        #     print('Не удалось загрузить файл')
        # bar.next()
    # bar.finish()
    return soup, resources


def load_page(content, path_to_file):
    try:
        with open(path_to_file, 'wb') as file:
            file.write(content)
    except PermissionError as e:
        # logger.error('Нет прав на внесение изменений', exc_info=True)
        raise KnownError('Нет прав на внесение изменений') from e
    # else:
        # logger.info('Страница успешно загружена')


def load_local_content(resources):
    bar = IncrementalBar(f'Loading page:', max=len(resources))
    for resource in resources:
        fileurl, filepath = resource
        try:
            if os.path.isfile(filepath):
                filepath += '_'
            session = requests.Session()
            local = session.get(fileurl)
            if 'css' in local.headers['content-type'] or \
                    'javascript' in local.headers['content-type']:
                # print(local.headers['content-type'])
                save_to_file(filepath, local.text, TEXT)
                # with open(filepath, 'w') as file:
                #     file.write(local.text)
                bar.next()
            else:
                save_to_file(filepath, local.content, BIN)
                # with open(filepath, 'wb') as file:
                #     # print(filebin.headers['content-type'])
                #     file.write(local.content)
                bar.next()
        except Exception:
            # logger.warning('Нет прав на внесение изменений', exc_info=True)
            print('Не удалось загрузить файл')
    bar.finish()


def save_page(url, output, logging_level):
    logger = logging.setup(logging_level=logging_level)
    logger.debug('Старт загрузки')
    response = get_response(url, logging_level)
    soup = BeautifulSoup(response, features="lxml")
    content_folder_name = make_page_name(url) + '_files'
    content_folder_path = os.path.join(output, content_folder_name)
    logger.info('Поиск и загрузка контента')
    # new_content, resources = make_local(response, output)
    resources = []
    for tag_name, attribute in SOURCE.items():
        soup, res = soup_find_save(url, content_folder_path, soup, logging_level, tag2find=tag_name, inner=attribute)
        resources += res
    # logger.info('Поиск и загрузка ссылок')
    # soup = soup_find_save(url, folder_path, soup,
    #                       logging_level, tag2find='link', inner='href')
    # logger.info('Загрузка скриптов')
    # soup = soup_find_save(url, folder_path, soup,
    #                       logging_level, tag2find='script', inner='src')
    page_name = make_page_name(url) + '.html'
    path_to_file = os.path.join(output, page_name)
    logger.debug(path_to_file)
    # try:
    #     with open(path_to_file, 'wb') as file:
    #         file.write(soup.prettify('utf-8'))
    # except PermissionError as e:
    #     logger.error('Нет прав на внесение изменений', exc_info=True)
    #     raise KnownError('Нет прав на внесение изменений') from e
    # else:
    #     logger.info('Страница успешно загружена')
    save_to_file(path_to_file, soup.prettify('utf-8'), BIN)
    create_dir(content_folder_path)
    load_local_content(resources)
    return path_to_file, content_folder_name


def transform_name(name, ending):
    return re.sub(r'[^0-9a-zA-Z]', '-', name) + ending


def create_dir(full_dir_name):
    try:
        os.mkdir(full_dir_name)
    except IOError as error:
        # logging.debug(traceback.format_exc(10))
        # logging.error("Can't create directory {}".format(full_dir_name))
        raise KnownError() from error


def get_content(url, priority):
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.RequestException as error:
        # logging.debug(traceback.format_exc(10))
        if priority == OBLIGATORY:
            # logging.error("Can't get {}".format(url))
            raise KnownError() from error
        else:
            # Some resources may not be available.
            # Let's give the program opportunity to finish.
            # logging.debug("Can't get {}".format(url))
            return
    return r.content


def make_local(content, dir_name):
    soup = BeautifulSoup(content, features='lxml')
    resources = []
    for tag_name, attribute in SOURCE.items():
        tags = soup.find_all([tag_name])
        for tag in tags:
            resource_url = tag.get(attribute)
            if resource_url and resource_url[0] == '/':
                resource_url_root, resource_url_ext = os.path.splitext(resource_url[1:]) # noqa E501
                resource_file_name = transform_name(resource_url_root, resource_url_ext) # noqa E501
                resources.append((resource_url, resource_file_name))
                # print((resource_url, resource_file_name))
                # change url to local path
                tag[attribute] = os.path.join(dir_name, resource_file_name) # noqa E501
    new_content = soup.prettify()
    return new_content, resources


def save_to_file(full_file_name, content, format):
    write_mode = "w" if format == TEXT else 'wb'
    # logging.info("Saving {}".format(full_file_name))
    try:
        with open(full_file_name, write_mode) as output_file:
            output_file.write(content)
    except IOError as error:
        # logging.debug(traceback.format_exc(10))
        # logging.error("Can't create file {}".format(full_file_name))
        raise KnownError() from error


def download_resources(url, target_dir, resources):
    files_count = len(resources)
    url_components = urlparse(url)
    bar = IncrementalBar('Loading:', suffix='%(percent)d%%', max=files_count)
    for resource in resources:
        resource_url, resource_file_name = resource
        resource_full_url = url_components._replace(path=resource_url).geturl() # noqa E501
        full_resource_name = os.path.join(target_dir, resource_file_name) # noqa E501
        resource_content = get_content(resource_full_url, priority=OBLIGATORY)
        if resource_content:
            save_to_file(full_resource_name, resource_content, BIN)
        bar.next()
    bar.finish()


def load_page(url, output):
    output = "" if output is None else output
    url_components = urlparse(url)
    address = url_components.netloc + url_components.path
    file_name = transform_name(address, '.html')
    dir_name = transform_name(address, '_files')
    full_file_name = os.path.join(output, file_name)
    full_dir_name = os.path.join(output, dir_name)
    create_dir(full_dir_name)
    file_content = get_content(url, OBLIGATORY)
    new_content, resources = make_local(file_content, dir_name)
    save_to_file(full_file_name, new_content, TEXT)
    download_resources(url, full_dir_name, resources)
