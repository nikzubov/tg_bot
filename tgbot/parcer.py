import requests
from bs4 import BeautifulSoup

anecdote_from_parce = []

url = 'https://anekdoty.ru/'
requests = requests.get(url)

soup = BeautifulSoup(requests.text, 'html.parser')

filter_html = soup.find_all('div', class_="holder-body")

for elem in filter_html:
    anecdote_from_parce.append(elem.text)