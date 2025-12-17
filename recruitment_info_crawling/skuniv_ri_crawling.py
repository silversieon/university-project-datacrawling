from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

def load_current_page(wd):
    html = wd.page_source
    soupSR = BeautifulSoup(html, "html.parser")

    results = []

    tbody = soupSR.select_one("tbody.post-list-body")
    if not tbody:
        return results

    rows = tbody.select("tr.post-td")

    for row in rows:
        tds = row.find_all("td")

        number = tds[0].get_text(strip=True)
        title = tds[1].get_text(strip=True)

        results.append({
            "number": number,
            "title": title
        })

    return results

def click_next_page(wd):
    spans = wd.find_elements(By.CSS_SELECTOR, "div.pager-wrap span")

    for span in spans:
        if span.text.strip() == ">":
            wd.execute_script("arguments[0].click();", span)
            return True

    return False

def skuniv_recruitment_info_crawling():
    wd = webdriver.Chrome()
    wd.get("https://job.skuniv.ac.kr/recruit-skuniv/")
    time.sleep(2)
    
    all_results = []
    page = 1

    while True:
        print(f"교내 채용 정보 {page}페이지 크롤링 중..")

        page_data = load_current_page(wd)
        all_results.extend(page_data)

        time.sleep(1)

        if not click_next_page(wd):
            print("교내 채용 정보 마지막 페이지에 도달하여 크롤링을 종료합니다.")
            break

        time.sleep(1)
        page += 1
    
    return all_results


df = pd.DataFrame(skuniv_recruitment_info_crawling())
df.to_csv("../recruitment_info_analysis/skuniv_recruitment_titles.csv", index=False, encoding="utf-8-sig")

print(f"크롤링된 채용정보 글 수: {len(df)}")
print("skuniv_recruitment_titles.csv 저장 완료")