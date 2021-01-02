import time
import requests
import pandas as pd
from bs4 import BeautifulSoup


# Block 1, try to get tanggal, judul, and link for every article
print('Block 1, try to get tanggal, judul, and link for every article')
tanggal = []
judul = []
link = []


def get_articles(url, sleep_time):
    # make request, and parse it to soup
    page = requests.get(url)
    time.sleep(sleep_time)
    soup = BeautifulSoup(page.content, 'html.parser')

    articles = soup.find_all('article', class_='card')
    return articles


p = 1
while True:
    # create url
    url = 'https://covid19.go.id/p/hoax-buster?page='
    url += str(p)

    # try looking for articles
    sleep_time = 1
    articles = get_articles(url=url, sleep_time=sleep_time)
    print(url, 'Artikel ditemukan :', len(articles))

    while len(articles) == 0:
        sleep_time += 1
        print('Mencoba akses url lagi dengan sleep_time=' + str(sleep_time) + '.')
        articles = get_articles(url=url, sleep_time=sleep_time)
        print(url, 'Artikel ditemukan :', len(articles))
        if sleep_time == 4:
            print('Artikel tidak ditemukan. Berhenti mencari.')
            break

    if len(articles) == 0:
        break

    # loop for every articles and scrape tanggal, judul, link
    for article in articles:
        tgl = article.find_all('time')[0].text
        tanggal.append(tgl)

        jdl = article.find_all('a', class_='text-color-dark')[0].text
        judul.append(jdl)

        lnk = article.find_all('a', class_='text-color-dark', href=True)[0]['href']
        link.append(lnk)

    p += 1


# Block 2, list tanggal, judul, and link convert to dataframe
print('Block 2, list tanggal, judul, and link convert to dataframe')
data = pd.DataFrame()
data['tanggal'] = tanggal
data['judul'] = judul
data['link'] = link

d = {
    'Jan': '1',
    'Feb': '2',
    'Mar': '3',
    'Apr': '4',
    'Mei': '5',
    'Jun': '6',
    'Jul': '7',
    'Agu': '8',
    'Sep': '9',
    'Okt': '10',
    'Nov': '11',
    'Des': '12'
}
for t, n in d.items():
    data.tanggal = data.tanggal.str.replace(t, n)
data.tanggal = pd.to_datetime(data.tanggal, dayfirst=True)
data.tanggal = data.tanggal.dt.date
print('Dataframe to CSV')
data.to_csv('data.csv', index=False)
print('Done... You now have the data.')
