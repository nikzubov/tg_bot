import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('.env'))

import aiohttp

yandex_gpt_api_url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'


async def get_query(query: str):
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
    url = yandex_gpt_api_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {os.getenv('KEY')}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=prompt, ssl=False) as response:
            response.raise_for_status()
            data = await response.json()
            return data['result']['alternatives'][0]['message']['text']
