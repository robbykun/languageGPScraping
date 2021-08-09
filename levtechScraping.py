import requests
from bs4 import BeautifulSoup

# スクレイピング対象の URL にリクエストを送り HTML を取得する
res = requests.get('https://freelance.levtech.jp/project/search/?keyword=&district[]=1&area[]=1&area[]=2&area[]=3&area[]=4&area[]=5&area[]=6&area[]=7&area[]=8&area[]=9&area[]=10&area[]=11&area[]=12&area[]=13&area[]=14&area[]=15&area[]=16&sala=7')

# レスポンスの HTML から BeautifulSoup オブジェクトを作る
soup = BeautifulSoup(res.text, 'html.parser')

# ページに含まれるリンクを全て取得する
links = [url.get('href') for url in soup.find_all('a')]

# 詳細のURLから「単価」を取得
for link in links:
    if str(link).startswith('/project/detail'):
        res = requests.get('https://freelance.levtech.jp' + link)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 単価
        unit_price = soup.find_all('em', {'class': 'js-yen'})
        print(unit_price)
