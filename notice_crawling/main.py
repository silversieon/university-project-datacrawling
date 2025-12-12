import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

BASE_URL = "https://www.skuniv.ac.kr"
START_YEAR = 2024  # 크롤링을 시작할 연도
FILE_NAME = f"skuniv_notice_{START_YEAR}_2025.csv"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_notices():
    page = 1
    all_data = []
    is_crawling = True

    print(f"크롤링 시작")

    while is_crawling:
        url = f"https://www.skuniv.ac.kr/notice/page/{page}"
        print(f"{page} 페이지")

        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(response.status_code)
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('table.board-list-table tbody tr')

            if not rows:
                break

            for row in rows:
                info_divs = row.select('td.post-info .post-info-wrap > div')
                
                date_text = "0000-00-00"
                view_count = "0"

                if len(info_divs) >= 3:
                    date_text = info_divs[2].text.strip()
                
                try:
                    year = int(date_text.split('-')[0])
                except:
                    year = 9999 

                is_pinned = "is-notice" in row.get('class', [])
                
                if not is_pinned and year < START_YEAR:
                    print(f"크롤링을 종료합니다.")
                    is_crawling = False
                    break
                
                if year < START_YEAR:
                    continue

                if info_divs:
                    raw_view = info_divs[-1].text.strip()
                    view_count = re.sub(r'[^0-9]', '', raw_view)

                title_tag = row.select_one('td.post-title a')
                if not title_tag:
                    continue

                title = title_tag.text.strip()
                link = title_tag['href']
                if link.startswith('/'):
                    link = BASE_URL + link

                all_data.append({
                    '작성일': date_text,
                    '제목': title,
                    '조회수': view_count,
                })

            page += 1
            time.sleep(random.uniform(0.3, 0.7)) 

        except Exception as e:
            print(e)
            break

    return all_data

result_data = crawl_notices()

if result_data:
    df = pd.DataFrame(result_data)
    
    df.sort_values(by='작성일', ascending=False, inplace=True)

    df.to_csv(FILE_NAME, index=False, encoding='utf-8-sig')
    
    print("-" * 60)
    print(f"총 {len(df)}개의 공지사항을 수집했습니다.")
    print(f"파일 저장: {FILE_NAME}")
else:
    print("수집된 데이터가 없습니다.")