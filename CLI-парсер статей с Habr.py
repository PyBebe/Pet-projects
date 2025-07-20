import typer
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

app = typer.Typer()

@app.command()
def scrape_habr(
    query: str = typer.Argument(..., help='Поисковый запрос (например, "python")'),
    pages: int = typer.Option(1, help='Количество страниц для обхода')
):
    """
    Парсер статей с Habr по поисковому запросу.
    """
    base_url = 'https://habr.com'
    param_1 = '/ru/search/page'
    param_2 = '/?q='
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    session = requests.Session()
    all_links = []
    for i in range(1, pages + 1):
        response = session.get(f'{base_url}{param_1}{i}{param_2}{query}', headers=headers)
        time.sleep(random.uniform(0.2, 0.5))
        soup = BeautifulSoup(response.text, 'html.parser')
        news = soup.find_all('article', class_='tm-articles-list__item')
        for j in news:
            link = base_url + j.find('h2').find('a').get('href')
            all_links.append(link)
    unique_links = set(all_links)
    
    rows = []
    for idx, link in enumerate(unique_links, 1):
        print(f'Прогресс: {round(idx * 100 / len(unique_links), 2)} %')
        try:
            article = BeautifulSoup(session.get(link, headers=headers).text, 'html.parser')
            time.sleep(random.uniform(0.2, 0.5))
            date = datetime.strptime(article.find('time').get('datetime'), '%Y-%m-%dT%H:%M:%S.%fZ')
            title = article.find('h1').find('span').text
            text = article.select_one('div.article-formatted-body').get_text(' ', strip=True)
            rating = article.find('div', class_='tm-votes-meter votes-switcher').find('span').text
            rows.append({'utc_date': date, 'title': title, 'link': link, 'text': text, 'rating': rating})
        except Exception as e:
            print(f'Ошибка при обработке статьи {link}: {e}')
    df = pd.DataFrame(rows)
    
    filename = f'habr_news_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx'
    df.sort_values('utc_date', ascending=False).to_excel(filename, index=False)
    print(f'\nГотово! Сохранено в файл: {filename}')

if __name__ == '__main__':
    app()
