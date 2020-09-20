from page_loader.load import make_page_name, save_page, KnownError
from tests.constants import TEST_DIR_PATH
import os
import tempfile
import pytest


test_url = 'https://ru.hexlet.io/courses'
test_dir = os.path.join(TEST_DIR_PATH, 'fixtures')
expected_filename = 'ru-hexlet-io-courses'
non_exist_path = 'non/exist/path'
wrong_schema_url = 'htts://ru.hexlet.io/courses'
wrong_hostname_url = 'https://ru.helet.io/courses'
missing_schema_url = 'ru.hexlet.io/courses'
response_404_url = 'https://httpbin.org/status/404'
response_503_url = 'https://httpbin.org/status/503'

check = {
    'http://ru.hexlet.io/courses': ('ru-hexlet-io-courses.html', 'ru-hexlet-io-courses_files'),
    'https://ru.hexlet.io': ('ru-hexlet-io.html', 'ru-hexlet-io_files'),
    'https://yandex.ru': ('yandex-ru.html', 'yandex-ru_files'),
}


def test():
    for key, item in check.items():
        with tempfile.TemporaryDirectory() as temp:
            result = save_page(key, temp, logging_level='debug')
            assert os.path.join(temp, result[0]) == os.path.join(temp, item[0])
            assert os.path.join(temp, result[1]) == os.path.join(temp, item[1])
            assert os.path.isfile(os.path.join(temp, result[0])) is True
            assert os.path.exists(os.path.join(temp, result[1])) is True


def test_make_pagename():
    page_name = make_page_name(test_url)
    assert page_name == expected_filename


def test_exceptions():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(KnownError):
            save_page(url=test_url, output='/tes', logging_level='debug')
        with pytest.raises(KnownError):
            save_page(url=test_url, output=non_exist_path, logging_level='debug')
        with pytest.raises(KnownError):
            save_page(url=wrong_schema_url, output=tmpdir, logging_level='debug')
        with pytest.raises(KnownError):
            save_page(url=missing_schema_url, output=tmpdir, logging_level='debug')
        with pytest.raises(KnownError):
            save_page(url=response_404_url, output=tmpdir, logging_level='debug')
        with pytest.raises(KnownError):
            save_page(url=response_503_url, output=tmpdir, logging_level='debug')
