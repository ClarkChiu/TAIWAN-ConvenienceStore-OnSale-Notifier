import os
import re
import pytest
from unittest import mock
from onsale_notifier.BasicFuncs import BasicFuncs


def test_get_seven_onsales_images(httpserver):
    images_list_file_path = 'tests/data/202012151030_seven_onsale_page.txt'
    with open(images_list_file_path, 'r', encoding='UTF-8') as f:
        images_list = f.read()

    seven_webpage_path = 'tests/data/202012151030_seven_onsale_page.html'
    with open(seven_webpage_path, 'r', encoding='UTF-8') as f:
        httpserver.serve_content(f.read())

    basic_func = BasicFuncs()
    basic_func.checkpoint_filepath = 'checkpoint/testing.checkpoint'
    basic_func.seven_base_url = httpserver.url
    image_urls = basic_func.get_seven_onsale_image_urls()
    image_urls = [
        url.replace(
            httpserver.url, 'https://www.7-11.com.tw'
        ) for url in image_urls
    ]
    assert images_list == '\n'.join(image_urls)


def test_create_telegram_send_conf():
    basic_func = BasicFuncs()
    basic_func.create_telegram_send_conf()
    with open('telegram-send.conf', 'r') as conf_file:
        assert re.match(
            (
                r'\[telegram\]\n'
                r'token = [0-9]{10}:[a-zA-Z0-9_-]{35}\n'
                r'chat_id = [\-\@\w\_]+'
            ),
            conf_file.read()
        )


def test_create_telegram_send_conf_without_env_var():
    basic_func = BasicFuncs()
    telegram_to = os.environ['TELEGRAM_TO']

    with pytest.raises(Exception):
        del os.environ['TELEGRAM_TO']
        basic_func.create_telegram_send_conf()

    os.environ['TELEGRAM_TO'] = telegram_to


def test_create_checkpoint():
    basic_func = BasicFuncs()
    basic_func.checkpoint_filepath = 'checkpoint/testing.checkpoint'
    basic_func.create_checkpoint(['News', 'List'])

    with open(basic_func.checkpoint_filepath, 'r'):
        pass


def test_get_saved_urls():
    basic_func = BasicFuncs()
    basic_func.checkpoint_filepath = 'checkpoint/testing.checkpoint'
    saved_news = basic_func.get_saved_urls()
    assert len(saved_news) != 0
    os.remove(basic_func.checkpoint_filepath)


def test_get_saved_urls_not_exists():
    basic_func = BasicFuncs()
    basic_func.checkpoint_filepath = 'checkpoint/20201017.checkpoint'
    saved_news = basic_func.get_saved_urls()
    assert len(saved_news) == 0


def test_image_downloader(requests_mock):
    basic_func = BasicFuncs()
    image_filename = 'test_image.jpg'
    image_filepath = f'{basic_func.image_path}/{image_filename}'
    image_test_content = 'Test Image'
    requests_mock.get(
        f'http://127.0.0.1/{image_filename}',
        text=image_test_content
    )
    basic_func.image_downloader([f'http://127.0.0.1/{image_filename}'])

    with open(image_filepath, 'r') as f:
        image_content = f.read()

    assert os.path.exists(image_filepath)
    assert image_content == image_test_content


@mock.patch('onsale_notifier.BasicFuncs.send')
def test_send_notification(telegram_send_send_action):
    basic_func = BasicFuncs()
    basic_func.send_notification()
    telegram_send_send_action.assert_called_once()
