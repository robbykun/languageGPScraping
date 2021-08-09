import requests
import concurrent.futures
from bs4 import BeautifulSoup


# 区切り文字
DELIMITER = '###'
# MAXプロセス数
PROC_IDX = 15
# レバテックURL
levtech_url = 'https://freelance.levtech.jp/project/search/?keyword=&district[]=1&area[]=1&area[]=2&area[]=3&area[]=4&area[]=5&area[]=6&area[]=7&area[]=8&area[]=9&area[]=10&area[]=11&area[]=12&area[]=13&area[]=14&area[]=15&area[]=16&sala=7'

#--------------------------------
# 案件の詳細ページ毎の情報を取得する関数
# param : 案件詳細ページのリンクオブジェクト
def get_project_detail(link):
    
    project_tsv = ''

    # 案件のリンクかチェック
    if str(link).startswith('/project/detail'):
        # 案件コード
        project_tsv += str(link).split('/')[3] + '\t'
        
        # 案件詳細取得
        res = requests.get('https://freelance.levtech.jp' + link)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 単価
        unit_price = soup.find('em', {'class': 'js-yen'})
        project_tsv += unit_price.text.replace('円', '') + '\t'

        # 最寄り駅
        for station in soup.find_all('p', {'class': 'pjtSummary__row__desc'}):
            if str(station.text).endswith("（東京都）"):
                project_tsv += station.text

        project_tsv += DELIMITER

        # プログラミング言語
        lang_csv = ''
        for lang in soup.find_all('a', {'class': 'pjtTag'}):
            if str(lang.get('href')).startswith('/project/skill'):
                # 余分なタブを入れない
                if len(lang_csv) > 0 : lang_csv += '\t'
                lang_csv += lang.text
        
        # 改行コードをフィックス
        project_tsv += lang_csv + '\n' 

    return project_tsv

#--------------------------------
# メインの処理
# 「Next」リンクが有効なら続行

while len(levtech_url) > 0 :

    # レバテックの案件一覧(23区で絞り込み)URL
    res = requests.get(levtech_url)

    # レスポンスの HTML から BeautifulSoup オブジェクトを作る
    soup = BeautifulSoup(res.text, 'html.parser')

    # 「Next」リンクが有効なら格納
    next_page = soup.find('a', {'rel': 'next'}).get('href')
    levtech_url = '' if next_page is None else 'https://freelance.levtech.jp' + next_page

    # ページに含まれるリンクを全て取得する
    links = [url.get('href') for url in soup.find_all('a', {'class': 'js-link_rel'})]

    # 案件一覧１ページ分のTSV
    project_tsv = ''
    
    # 案件詳細から情報取得(マルチプロセス)
    with concurrent.futures.ProcessPoolExecutor(max_workers=PROC_IDX) as executor:
        futures = [executor.submit(get_project_detail,link) for link in links]

        # 詳細情報が取得できた順に格納
        for future in concurrent.futures.as_completed(futures):
            project_tsv += future.result()


    print(project_tsv)
    # TODO：GoにRestApiする
