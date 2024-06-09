import logging
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.env'))

import aiohttp


async def get_response(query: str) -> str:
    prompt = {
        "modelUri": f"gpt://{os.getenv('CATALOGUE_ID')}/yandexgpt",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": f"{query}"
            },
        ]
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {os.getenv('KEY')}"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=prompt, ssl=False) as response:
                response.raise_for_status()
                data = await response.json()
                return data['result']['alternatives'][0]['message']['text']
        except aiohttp.ClientError as e:
            logging.error(e)
