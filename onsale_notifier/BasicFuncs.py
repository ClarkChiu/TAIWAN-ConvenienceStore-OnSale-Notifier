import os
import time
import shutil
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from telegram_send import send
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BasicFuncs(object):
    """docstring for BasicFuncs."""

    def __init__(self):
        self.checkpoint_filepath = './checkpoint/images_url.log'
        self.image_path = './images'
        self.seven_base_url = 'https://www.7-11.com.tw'
        self.get_web_waiting_time = 15
        self.chrome_options = Options()
        self.chrome_options.headless = True
        self.chrome_options.add_argument(
            'User-Agent={}'.format(
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/39.0.2171.95 '
                'Safari/537.36'
            )
        )

        self.telegram_send_interval = 5

    def get_seven_onsale_image_urls(self):
        with webdriver.Chrome(options=self.chrome_options) as web:
            web.get(urljoin(self.seven_base_url, '/7app/coupon/line.html'))
            time.sleep(self.get_web_waiting_time)
            seven_onsale_page_source = web.page_source

        seven_page_soup = BeautifulSoup(
            seven_onsale_page_source, 'html.parser'
        )

        image_urls = []
        div_image_uris = seven_page_soup.find('div', class_='coupon')
        saved_urls = self.get_saved_urls()
        for image_uri in div_image_uris:
            condition = (
                image_uri['src'] not in saved_urls
                and not image_uri.has_attr('style')
            )

            if condition:
                image_urls.append(
                    urljoin(
                        self.seven_base_url, f"/7app/coupon/{image_uri['src']}"
                    )
                )

        return image_urls

    def image_downloader(self, image_urls):
        headers = {
            'user-agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/39.0.2171.95 '
                'Safari/537.36'
            )
        }
        os.makedirs(self.image_path, exist_ok=True)

        for image_url in image_urls:
            filename = f'./images/{image_url.split("/")[-1]}'
            with requests.get(image_url, headers=headers, stream=True) as r:
                with open(filename, "wb") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

    def create_telegram_send_conf(self):
        telegram_token = os.getenv('TELEGRAM_TOKEN')
        telegram_to = os.getenv('TELEGRAM_TO')

        if not telegram_token or not telegram_to:
            raise Exception(
                'The telegram-send related info are not in env variable'
            )

        with open('telegram-send.conf', 'w') as conf_file:
            conf_file.write(
                '[telegram]\n'
                f'token = {telegram_token}\n'
                f'chat_id = {telegram_to}'
            )

    def send_notification(self):
        for filename in os.listdir(self.image_path):
            filepath = os.path.join(self.image_path, filename)
            with open(filepath, 'rb') as f:
                send(images=[f], conf='telegram-send.conf')
            time.sleep(self.telegram_send_interval)

    def create_checkpoint(self, url_list):
        os.makedirs(
            os.path.dirname(self.checkpoint_filepath), exist_ok=True
        )

        with open(self.checkpoint_filepath,
                  'a+',
                  encoding='utf-8') as check_point_file:
            check_point_file.write('\n'.join(url_list))

    def get_saved_urls(self):
        try:
            with open(self.checkpoint_filepath,
                      'r+',
                      encoding='utf-8') as check_point_file:
                saved_urls = check_point_file.read()

            return saved_urls
        except Exception:
            return ''
