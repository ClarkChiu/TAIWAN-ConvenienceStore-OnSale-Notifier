import shutil
from BasicFuncs import BasicFuncs


basic_func = BasicFuncs()
image_urls = basic_func.get_seven_onsale_image_urls()
basic_func.image_downloader(image_urls)
basic_func.create_telegram_send_conf()
basic_func.send_notification()
basic_func.create_checkpoint(image_urls)
shutil.rmtree(basic_func.image_path)
