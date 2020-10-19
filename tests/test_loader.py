import os
import tempfile

import pytest
from page_loader import logging
from page_loader import loader
from bs4 import BeautifulSoup


def read(file):
    with open(file, 'r') as input_file:
        answer = input_file.read()
    return answer


TEST_URL = 'https://ru.hexlet.io/courses'
LOCAL_CONTENT = (
    'https://ru.hexlet.io/assets/application.4 min.css?weger=wefwe&erer=ref',
    'assets-application_4_min.css'
)
EXPECTED_FILENAME = 'ru-hexlet-io-courses.html'
NON_EXIST_PATH = 'non/exist/path'
WRONG_SCHEMA_URL = 'htts://ru.hexlet.io/courses'
WRONG_HOSTNAME_URL = 'https://ru.helet.io/courses'
MISSING_SCHEMA_URL = 'ru.hexlet.io/courses'
RESPONSE_404_URL = 'https://httpbin.org/status/404'
RESPONSE_503_URL = 'https://httpbin.org/status/503'
URL = 'https://roman-sergeichuk.github.io/python-project-lvl3'
EXPECTED_DIRECTORY_NAME = 'roman-sergeichuk-github-io-python-project-lvl3_files'
EXPECTED_PAGE_NAME = 'roman-sergeichuk-github-io-python-project-lvl3.html'
SAMPLE_SITE = './tests/fixtures/sample_site.html'
CONTENT = ('application.css', 'application.js', 'bootstrap_min.css', 'logo.png')

logging.setup(logging_level='debug')


def test_load_page():
    with tempfile.TemporaryDirectory() as temp:
        response = loader.get_response(URL)
        assert read(SAMPLE_SITE) == response.text
        content_folder_name = loader.make_page_name(URL, loader.FILES)
        assert content_folder_name == EXPECTED_DIRECTORY_NAME
        content_folder_path = os.path.join(temp, content_folder_name)
        soup = BeautifulSoup(response.text, features="lxml")
        resources = loader.collect_all_resources(URL, content_folder_path, soup)
        page_name = loader.make_page_name(URL, loader.HTML)
        assert page_name == EXPECTED_PAGE_NAME
        path_to_file = os.path.join(temp, page_name)
        loader.save_to_file(path_to_file, soup.prettify('utf-8'))
        assert os.path.isfile(path_to_file)
        loader.create_dir(content_folder_path)
        assert os.path.isdir(content_folder_path)
        for resource in resources:
            loader.load_local_content(resource)
        assert len(resources) == len(CONTENT)
        for file in CONTENT:
            filepath = os.path.join(content_folder_path, file)
            assert os.path.isfile(filepath)


def test_make_pagename():
    page_name = loader.make_page_name(TEST_URL, loader.HTML)
    assert page_name == EXPECTED_FILENAME


def test_make_local_content_name():
    url, expected_name = LOCAL_CONTENT
    name = loader.make_inner_filename(url)
    assert name == expected_name


def test_exceptions():
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(loader.KnownError):
            loader.save_page(url=TEST_URL, output='/tes')
        with pytest.raises(loader.KnownError):
            loader.save_page(url=TEST_URL, output=NON_EXIST_PATH)
        with pytest.raises(loader.KnownError):
            loader.save_page(url=WRONG_SCHEMA_URL, output=tmpdir)
        with pytest.raises(loader.KnownError):
            loader.save_page(url=MISSING_SCHEMA_URL, output=tmpdir)
        with pytest.raises(loader.KnownError):
            loader.save_page(url=RESPONSE_404_URL, output=tmpdir)
        with pytest.raises(loader.KnownError):
            loader.save_page(url=RESPONSE_503_URL, output=tmpdir)
