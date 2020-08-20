from page_loader.load import make_filename, load_content
from tests.constants import TEST_DIR_PATH
import os
#import pytest


# @pytest.fixture
# def get_fixture(file_name):
#     fixture = os.path.join(TEST_DIR_PATH, 'fixtures', file_name)
#     return fixture


test_url = 'http://rsergeichuk.pythonanywhere.com/dashboard/'
test_dir = os.path.join(TEST_DIR_PATH, 'fixtures')
expected_filename = 'rsergeichuk-pythonanywhere-com-dashboard.html'


def test_loader():
    response = load_content(test_url)
    directory = test_dir
    if directory:
        directory += '/'
    file_name = make_filename(test_url)
    with open(f'{directory}{file_name}', 'w') as file:
        file.write(response.text)
    assert file_name == expected_filename
