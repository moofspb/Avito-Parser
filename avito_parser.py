import urllib.request
import csv
from bs4 import BeautifulSoup


BASE_URL = 'https://www.avito.ru'
CITY = '/sankt-peterburg?'
QUERY = '&bt=1&i=1&q=macbook+pro+13'


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def get_page_count(html):
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.find('div', class_='pagination-pages clearfix')
    return int(pagination.find_all('a')[-2].text)


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    table_before = soup.find('div', class_='js-catalog_before-ads')
    table_after = soup.find('div', class_='js-catalog_after-ads')

    ads_before = []
    ads_after = []

    for row in table_before.find_all('div', class_='description'):
        title = row.find('a', class_='item-description-title-link')
        price = row.find('div', class_='about')
        date = row.find('div', class_='c-2')
        other = row.find('div', class_='data')

        ads_before.append({
            'title': title.text.strip(),
            'link': BASE_URL + title['href'],
            'price': price.text.strip(),
            'date': date.text.strip(),
            'extraInfo': [data.text.replace("\xa0", " ")
                          for data in other.find_all('p')]
        })

    for row in table_after.find_all('div', class_='description'):
        title = row.find('a', class_='item-description-title-link')
        price = row.find('div', class_='about')
        date = row.find('div', class_='c-2')
        other = row.find('div', class_='data')

        ads_after.append({
            'title': title.text.strip(),
            'link': BASE_URL + title['href'],
            'price': price.text.strip(),
            'date': date.text.strip(),
            'extraInfo': [data.text.replace("\xa0", " ")
                          for data in other.find_all('p')]
        })
    ads_before.extend(ads_after)

    return ads_before


def save_to_csv(ads, path):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('Наименование', 'Ссылка', 'Цена',
                        'Дата', 'Информация о продавце'))

        for ad in ads:
            writer.writerow((ad['title'], ad['link'], ad['price'], ad['date'],
                             ', '.join(ad['extraInfo'])))


def main():
    page_count = get_page_count(get_html(BASE_URL + CITY + QUERY))
    print('Pages found: %d' % page_count)

    ads = []

    for page in range(1, page_count + 1):
        print('Parsing %d%%' % (page / page_count * 100))
        ads.extend(parse(get_html(BASE_URL + CITY + 'p=%d' % page + QUERY)))

    save_to_csv(ads, 'ads.csv')


if __name__ == '__main__':
    main()
