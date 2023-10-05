import logging

from datetime import date
import os.path as path
from os import mkdir


def logging_enable(save_to_file: bool = False) -> None:
    """
    Функция включения логирования
    """
    if save_to_file:
        start_pth = path.join('data', 'logs')

        if not path.exists(start_pth):
            mkdir(start_pth)

        def generate_path_for_log(num: int) -> str:
            today = date.today().isoformat()
            file_name = f'{today}-{num}.log'
            return path.join(start_pth, file_name)

        count = 1
        pth = generate_path_for_log(count)

        while path.exists(pth):
            count += 1
            pth = generate_path_for_log(num=count)
    else:
        pth = None

    logging.basicConfig(level=logging.INFO,
                        filename=pth,
                        filemode='w',
                        encoding='utf-8',
                        format='%(asctime)s [%(module)s] %(levelname)s %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S'
                        )