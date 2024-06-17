import logging
from typing import List

import aiohttp
from config import settings


class GptClient:
    def __init__(
        self,
        url: str,
        catalogue_id: str,
        api_key: str
    ) -> None:
        self.url = url
        self.__catalogue_id = catalogue_id
        self.__api_key = api_key

    async def get_response(
        self, query: str,
        background: List[str] | None,
    ) -> str:
        messages = []
        if background:
            messages = [{
                'role': 'user'if i % 2 == 0 else 'assistant',
                'text': background[i]
                } for i in range(len(background))
            ]
        messages.append({
            'role': 'user',
            'text': query
        })
        prompt = {
            "modelUri": f"gpt://{self.__catalogue_id}/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.__api_key}"
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.url,
                    headers=headers,
                    json=prompt,
                    ssl=False
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data['result']['alternatives'][0]['message']['text']
            except aiohttp.ClientError as e:
                logging.error(e)
            return 'Произошла ошибка'


ya_client = GptClient(
    url='https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
    catalogue_id=settings.CATALOGUE_ID,
    api_key=settings.KEY
)
