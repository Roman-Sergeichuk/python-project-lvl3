import os
import tempfile

import pytest
from page_loader import logging

from page_loader.loader import (KnownError, make_inner_filename, make_page_name,
                                save_page)

TEST_DIR_PATH = os.path.dirname(__file__)

TEST_URL = 'https://ru.hexlet.io/courses'
TEST_LOCAL_CONTENT_PATH = 'https://ru.hexlet.io/assets/application.css'
EXPECTED_FILENAME = 'ru-hexlet-io-courses'
NON_EXIST_PATH = 'non/exist/path'
WRONG_SCHEMA_URL = 'htts://ru.hexlet.io/courses'
WRONG_HOSTNAME_URL = 'https://ru.helet.io/courses'
MISSING_SCHEMA_URL = 'ru.hexlet.io/courses'
RESPONSE_404_URL = 'https://httpbin.org/status/404'
RESPONSE_503_URL = 'https://httpbin.org/status/503'

check = (
    ('http://ru.hexlet.io/courses', 'ru-hexlet-io-courses.html', 'ru-hexlet-io-courses_files'),
    ('https://ru.hexlet.io', 'ru-hexlet-io.html', 'ru-hexlet-io_files'),
    ('https://yandex.ru', 'yandex-ru.html', 'yandex-ru_files')
)

logging.setup(logging_level='debug')


def test_page_load():
    for url, expected_content_folder, expected_html_file in check:
        with tempfile.TemporaryDirectory() as temp:
            result_folder, result_html = save_page(url, temp)
            assert os.path.join(temp, result_folder) == os.path.join(temp, expected_content_folder)
            assert os.path.join(temp, result_html) == os.path.join(temp, expected_html_file)
            assert os.path.isfile(os.path.join(temp, result_folder)) is True
            assert os.path.exists(os.path.join(temp, result_html)) is True


def test_make_pagename():
    page_name = make_page_name(TEST_URL)
    assert page_name == EXPECTED_FILENAME


def test_make_local_content_name():
    local_content_name = make_inner_filename(TEST_LOCAL_CONTENT_PATH)
    assert local_content_name == 'assets-application.css'


def test_exceptions():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(KnownError):
            save_page(url=TEST_URL, output='/tes')
        with pytest.raises(KnownError):
            save_page(url=TEST_URL, output=NON_EXIST_PATH)
        with pytest.raises(KnownError):
            save_page(url=WRONG_SCHEMA_URL, output=tmpdir)
        with pytest.raises(KnownError):
            save_page(url=MISSING_SCHEMA_URL, output=tmpdir)
        with pytest.raises(KnownError):
            save_page(url=RESPONSE_404_URL, output=tmpdir)
        with pytest.raises(KnownError):
            save_page(url=RESPONSE_503_URL, output=tmpdir)
