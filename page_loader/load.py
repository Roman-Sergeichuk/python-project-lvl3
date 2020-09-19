import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import os
import logging
import sys
from progress.bar import IncrementalBar


# def page_name(url):
#     parts_url = urlparse(url)
#     host_name = parts_url.netloc.replace('.', '-')
#     if parts_url.path:
#         path = parts_url.path.replace('/', '-')
#         name = re.sub('^(\.|-)$', '', f'{host_name}{path}')
#     else:
#         name = host_name
#     return name


class KnownError(Exception):
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

# Правильное название файлов
# def make_inner_filename(path_to_file):
#     parts_url = urlparse(path_to_file)
#     path_without_host = parts_url.path
#     path = os.path.dirname(path_without_host)
#     path = path.replace('/', '-')[1:]
#     if path:
#         path += '-'
#     origin_filename = os.path.basename(path_to_file)
#     file_name, extension = os.path.splitext(origin_filename)
#     final_filename = ''
#     for char in file_name:
#         final_filename += char
#         if len(final_filename) >= 200:
#             final_filename = path + final_filename + extension
#             break
#     else:
#         final_filename = path + final_filename + extension
#     return final_filename

# Хорошо скачивает википедию
def make_inner_filename(path_to_file):
    parts_url = urlparse(path_to_file)
    path_without_host = parts_url.path
    path = os.path.dirname(path_without_host)
    path = path.replace('/', '-')[1:]
    if path:
        path += '-'
    origin_filename = os.path.basename(path_to_file)
    file_name, extension = os.path.splitext(origin_filename)
    if '?' in extension:
        extension = extension.split('?')
    if '-' in extension:
        extension = extension.split('-')
    final_filename = ''
    if type(extension) == list:
        extension = extension[0]
        #print(extension)
        #re.sub(r'\W', '-', extension[1:])
    for char in file_name:
        final_filename += char
        if len(final_filename) >= 40:
            final_filename = final_filename + extension
            break
        else:
            # final_filename = re.sub(r'\W', '-', final_filename)
            final_filename = final_filename + extension
    #final_filename.replace('%28', '(').replace('%29', ')')
    return final_filename


def get_response(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response


def setup_log(logging_level, logfile='logfile.log'):
    if logging_level == 'debug' or logging_level == 'DEBUG':
        logging_level = logging.DEBUG
    elif logging_level == 'warning' or logging_level == 'WARNING':
        logging_level = logging.WARNING
    elif logging_level == 'error' or logging_level == 'ERROR':
        logging_level = logging.ERROR
    elif logging_level == 'critical' or logging_level == 'CRITICAL':
        logging_level = logging.CRITICAL
    else:
        logging_level = logging.INFO

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter_console = logging.Formatter('%(message)s')
    console.setFormatter(formatter_console)
    logger.addHandler(console)
    f = logging.FileHandler(logfile)
    f.setLevel(logging_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    f.setFormatter(formatter)
    logger.addHandler(f)
    return logger


def save_page(url, output, logging_level):
    logger = setup_log(logging_level=logging_level)
    logger.debug('Процесс запущен')

    def soup_find_save(pagefolder, tag2find='img', inner='src'):
        """saves on specified `pagefolder` all tag2find objects"""
        if not os.path.exists(pagefolder):  # create only once
            logger.debug('Пытаюсь создать папку с локальным контентом')
            try:
                os.mkdir(pagefolder, mode=0o700, dir_fd=None)
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
        bar = IncrementalBar('Loading:', max=files_count)
        for res in soup.findAll(tag2find):  # images, css, etc..
            try:
                # if not res.has_attr(inner):
                #     print('Атрибут отсутствует')
                #     continue  # may or may not exist
                inner_filename = make_inner_filename(res[inner])
                fileurl = urljoin(url, res.get(inner))
                filepath = os.path.join(pagefolder, inner_filename)
                # rename html ref so can move html and folder of files anywhere
                res[inner] = os.path.join(os.path.basename(pagefolder), inner_filename)  # noqa: E501
                logger.debug(inner_filename)
                if not os.path.isfile(filepath):  # was not downloaded
                    with open(filepath, 'wb') as file:
                        filebin = session.get(fileurl)
                        file.write(filebin.content)
            except Exception:
                logger.warning('file was not downloaded', exc_info=True)
            bar.next()
        bar.finish()
        return soup

    session = requests.Session()
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
    response.encoding = ''
    #soup = BeautifulSoup(response.text.replace('%28', '(').replace('%29', ')'), features="lxml")
    soup = BeautifulSoup(response.text, features="lxml")
    logger.debug(response.text)
    page_folder_name = make_page_name(url) + '_files'
    folder_path = os.path.join(output, page_folder_name)
    logging.info('Поиск и загрузка картинок')
    print('Поиск и загрузка картинок')
    soup = soup_find_save(folder_path, 'img', 'src')
    logging.info('Поиск и загрузка ссылок')
    print('Поиск и загрузка ссылок')
    soup = soup_find_save(folder_path, 'link', 'href')
    logging.info('Поиск и загрузка скриптов')
    print('Поиск и загрузка скриптов')
    soup = soup_find_save(folder_path, 'script', 'src')
    page_name = make_page_name(url) + '.html'
    path_to_file = os.path.join(output, page_name)
    logging.debug(path_to_file)
    try:
        with open(path_to_file, 'wb') as file:
            file.write(soup.prettify('utf-8'))
    except PermissionError as e:
        logging.error('Нет прав на внесение изменений', exc_info=True)
        raise KnownError('Нет прав на внесение изменений') from e
    else:
        logging.info('Страница успешно загружена')
    return path_to_file, page_folder_name
