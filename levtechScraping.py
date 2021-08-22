import sys
import time
import requests
import concurrent.futures
import dataclasses
from dataclasses_json import dataclass_json
from bs4 import BeautifulSoup


DELIMITER = '###'

MAX_PROC = 3

URL_REST_API = 'http://go:8080/project'

# レバテックURL
levtech_url = 'https://freelance.levtech.jp/project/search/?keyword=&district[]=1&area[]=1&area[]=2&area[]=3&area[]=4&area[]=5&area[]=6&area[]=7&area[]=8&area[]=9&area[]=10&area[]=11&area[]=12&area[]=13&area[]=14&area[]=15&area[]=16&sala=7'


#--------------------------------
# DTOクラス定義 Language
@dataclass_json
@dataclasses.dataclass
class Language:
    project_no: str
    language_type: str
#--------------------------------
# DTOクラス定義 Project
@dataclass_json
@dataclasses.dataclass
class Project:
    project_no: str = dataclasses.field(init=False)
    price: int = dataclasses.field(default=0,init=False)
    station: str = dataclasses.field(init=False)
    languages:list[Language] = dataclasses.field(default_factory=list,init=False)
#--------------------------------
# DTOクラス定義 Projects
@dataclass_json
@dataclasses.dataclass
class Projects:
    projects:list[Project] = dataclasses.field(default_factory=list,init=False)


#--------------------------------
# 案件の詳細ページ毎の情報を取得する関数
# param : 案件詳細ページのリンクオブジェクト
def get_project_detail(link):
    
    project = Project()

    # 案件のリンクかチェック
    if str(link).startswith('/project/detail'):
        # 案件コード
        project.project_no = str(link).split('/')[3]
        
        # 案件詳細取得
        res = requests.get('https://freelance.levtech.jp' + link)
        soup = BeautifulSoup(res.text, 'html.parser')

        # 単価
        unit_price = soup.find('em', {'class': 'js-yen'})
        if unit_price is None:
            print(project.project_no)
        else:
            project.price = int((unit_price.text.replace('円', '')).replace(',', ''))
            # 時間単価除外
            if project.price < 300_000:
                return None

        # 最寄り駅
        for station in soup.find_all('p', {'class': 'pjtSummary__row__desc'}):
            if str(station.text).endswith("（東京都）"):
                project.station =  station.text

        # プログラミング言語
        lang_tsv = ''
        for lang in soup.find_all('a', {'class': 'pjtTag'}):
            if str(lang.get('href')).startswith('/project/skill'):
                language = Language(project.project_no,lang.text)
                project.languages.append(language)
    return project

#--------------------------------
# メインの処理
#--------------------------------

Projects table and languages table record all delete.
response = requests.delete(URL_REST_API)
if response.status_code != 200 :
    print(str(response.status_code) + ' : Table all record delete error.')
    sys.exit(1)

# 「Next」リンクが有効なら続行
while len(levtech_url) > 0 :
    # 時間計測（１ページ当たり　START）
    start = time.time()

    # レバテックの案件一覧(23区で絞り込み)URL
    res = requests.get(levtech_url)

    # レスポンスの HTML から BeautifulSoup オブジェクトを作る
    soup = BeautifulSoup(res.text, 'html.parser')

    # ページに含まれるリンクを全て取得する
    links = [url.get('href') for url in soup.find_all('a', {'class': 'js-link_rel'})]

    # 案件一覧１ページ分リスト
    project_list = Projects()
    
    # 案件詳細から情報取得(マルチプロセス)
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_PROC) as executor:
        futures = [executor.submit(get_project_detail,link) for link in links]

        # 詳細情報が取得できた順に格納
        for future in concurrent.futures.as_completed(futures):
            if future.result() is not None:
                project_list.projects.append(future.result())

    # print(project_list.to_json(ensure_ascii=False))

    # GoのRestApiにPOSTする
    response = requests.post(
        URL_REST_API,
        project_list.to_json(),
        headers={'Content-Type': 'application/json'})

    # 「Next」リンクが有効なら格納
    next_page = soup.find('a', {'rel': 'next'}).get('href')
    levtech_url = '' if next_page is None else 'https://freelance.levtech.jp' + next_page

    # 時間計測（１ページ当たり　END）
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
