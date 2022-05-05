from time import time

import requests
import lxml
from bs4 import BeautifulSoup

import sys
import datetime
import json
import csv

models_data = []
cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')

def get_last_page():
	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36'
	}
	
	url = 'https://www.renderhub.com/3d-figures-and-assets'

	session = requests.Session()
	response = session.get(url=url, headers=headers)
	soup = BeautifulSoup(response.text, 'lxml')

	page_list = soup.find_all('div', class_='pageNum')

	return int(page_list[-2].get_text())

def get_page_data(session, page):

	with open(f'models_{cur_time}.csv', 'w', encoding='utf-8') as file:
		writer = csv.writer(file)

		writer.writerow(
			(
				'Название',
				'Ссылка на картинку',
				'Дата выхода',
				'Категория',
				'Ссылка на скачивание'
				)
			)


	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36'
	}

	url = f'https://daz4free.ru/catalog/{page}'

	response = session.get(url=url, headers=headers)
	soup = BeautifulSoup(response.text, 'lxml')
	temp = soup.find_all('div', {'class': ['uk-card', 'uk-card-default', 'uk-card-small', 'uk-transition-toggle', 'uk-scrollspy-inview', 'uk-animation-slide-bottom-small'], 'style': ''})
	for temp_card in temp:
		try:
			title = temp_card.find('h3').find('a').get('title')
			img = 'https://daz4free.ru' + temp_card.find('img').get('src')
			calendar = temp_card.find('li').get_text()[2:]
			download_link = 'https://daz4free.ru' + temp_card.find('a', {'class': ['uk-button', 'uk-button-primary', 'uk-button-small', 'uk-width-1-1']}).get('href')
			category = temp_card.find('div', {'class': ['uk-transition-slide-top', 'uk-position-top', 'uk-overlay-small', 'uk-overlay-default', 'uk-text-small', 'uk-text-primary']}).find_next_sibling().a.get_text()

			if title != None:
				#print(title)
				#print(img)
				#print(calendar)
				#print(category)
				#print(download_link)
				#print('-----------------------')
				models_data.append(
					{
						'model_title': title,
						'model_img': img,
						'model_calendar': calendar,
						'model_category': category,
						'model_download_link': download_link
					}
				)
		except AttributeError:
			pass

	with open(f'models_{cur_time}.json', 'w', encoding='utf-8') as file:
		json.dump(models_data, file, indent=4, ensure_ascii=False) #ensure_ascii=True - экранирование не-ASCII символов, indent=None - количество отступов при сериализации

	for model in models_data:
		with open(f'models_{cur_time}.csv', 'a', encoding='utf-8') as file:
			writer = csv.writer(file)

			writer.writerow(
				(
					title,
					img,
					calendar,
					category,
					download_link
					)
				)



async def gather_data():
	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36'
	}
	
	url = 'https://daz4free.ru/catalog'

	async with aiohttp.ClientSession() as session:
		response = await session.get(url=url, headers=headers)
		soup = BeautifulSoup(await response.text(), 'lxml')
		try:
			string = soup.find("li", string='»»').a.get('href')
		except AttributeError:
			print('Интернет урезан! Ты в локалке, вынь провод!')
		x = string.rfind('/') + 1
		last_page = int(string[x:])

		tasks = []

		for page in range(1, last_page):
			task = asyncio.create_task(get_page_data(session, page))
			tasks.append(task)

		await asyncio.gather(*tasks)

def gather_data():
	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36'
	}
	
	url = 'https://daz4free.ru/catalog'

	session = requests.Session()
	response = session.get(url=url, headers=headers)
	soup = BeautifulSoup(response.text, 'lxml')
	try:
		string = soup.find("li", string='»»').a.get('href')
	except AttributeError:
		print('Интернет урезан! Ты в локалке, вынь провод!')
	x = string.rfind('/') + 1
	last_page = int(string[x:])

	tasks = []

	for page in range(1, last_page):
		get_page_data(session, page)


def main():
	t1 = time() #засекаем секундомер (отключить весь вывод в консоль!)
	gather_data()
	t2 = time() - t1
	print(t2) #48.85 секунд

if __name__ == '__main__':
	main()