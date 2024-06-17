import logging
from typing import List

import aiohttp
from bot_instance import SCHEDULER
from bs4 import BeautifulSoup

anecdote_from_parce = []

url = 'https://anekdoty.ru/'

async def build_anec_list() -> None:
    '''Функция для обновления списка анекдотов anecdote_from_parce'''
    global anecdote_from_parce
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, ssl=False) as response:
                response.raise_for_status()
                data = await response.text()
    
                soup = BeautifulSoup(data, 'html.parser')
            
                filter_html = soup.find_all('div', class_="holder-body")
            
                for elem in filter_html:
                    anecdote_from_parce.append(elem.text)
                
                logging.info('Список анекдотов обновлен.')
        except aiohttp.ClientError as e:
            logging.error(e)


async def get_anec_list() -> List[str]:
    return anecdote_from_parce


SCHEDULER.add_job(build_anec_list, 'cron', hour=10)
