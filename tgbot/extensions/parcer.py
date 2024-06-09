import logging
from typing import List
import aiohttp
from bs4 import BeautifulSoup
from bot_instance import SCHEDULER


anecdote_from_parce = []

url = 'https://anekdoty.ru/'

async def build_anec_list() -> None:
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
