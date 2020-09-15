from page_loader.load import make_page_name, get_response, save_page
from tests.constants import TEST_DIR_PATH
import os
import tempfile
#import pytest


# @pytest.fixture
# def get_fixture(file_name):
#     fixture = os.path.join(TEST_DIR_PATH, 'fixtures', file_name)
#     return fixture


test_url = 'http://ru.hexlet.io/courses'
test_dir = os.path.join(TEST_DIR_PATH, 'fixtures')
expected_filename = 'ru-hexlet-io-courses'

check = {
    'http://ru.hexlet.io/courses': ('ru-hexlet-io-courses.html', 'ru-hexlet-io-courses_files'),
    'https://ru.hexlet.io': ('ru-hexlet-io.html', 'ru-hexlet-io_files'),
    'https://yandex.ru': ('yandex-ru.html', 'yandex-ru_files'),
}


def test():
    for key, item in check.items():
        with tempfile.TemporaryDirectory() as temp:
            result = save_page(key, temp)
            assert os.path.join(temp, result[0]) == os.path.join(temp, item[0])
            assert os.path.join(temp, result[1]) == os.path.join(temp, item[1])
            assert os.path.isfile(os.path.join(temp, result[0])) is True
            assert os.path.exists(os.path.join(temp, result[1])) is True


def test_loader():
    response = get_response(test_url)
    directory = test_dir
    if directory:
        directory += '/'
    file_name = make_page_name(test_url)
    with open(f'{directory}{file_name}', 'w') as file:
        file.write(response.text)
    assert file_name == expected_filename

