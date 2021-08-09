import requests
from bs4 import BeautifulSoup

# レバテックの案件一覧(23区で絞り込み)URL
res = requests.get('https://freelance.levtech.jp/project/search/?keyword=&district[]=1&area[]=1&area[]=2&area[]=3&area[]=4&area[]=5&area[]=6&area[]=7&area[]=8&area[]=9&area[]=10&area[]=11&area[]=12&area[]=13&area[]=14&area[]=15&area[]=16&sala=7')

# レスポンスの HTML から BeautifulSoup オブジェクトを作る
soup = BeautifulSoup(res.text, 'html.parser')

# ページに含まれるリンクを全て取得する
links = [url.get('href') for url in soup.find_all('a', {'class': 'js-link_rel'})]

# 案件詳細から情報取得
for link in links:
    # 案件のリンクかチェック
    if str(link).startswith('/project/detail'):
        # 案件コード
        print(str(link).split('/')[3])

        # 案件詳細取得
        res = requests.get('https://freelance.levtech.jp' + link)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 単価
        unit_price = soup.find('em', {'class': 'js-yen'})
        print(unit_price.text.replace('円', ''))

        # 最寄り駅
        for station in soup.find_all('p', {'class': 'pjtSummary__row__desc'}):
            if str(station.text).endswith("（東京都）"):
                print(station.text)

        # プログラミング言語
        for lang in soup.find_all('a', {'class': 'pjtTag'}):
            if str(lang.get('href')).startswith('/project/skill'):
                print(lang.text)
