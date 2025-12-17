from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# 최대 크롤링 페이지 및 최대 크롤링 제목 수
MAX_PAGES = 20
MAX_TITLES = 1000

# 목표 크롤링 카테고리 및 value
TARGET_CATEGORIES_MAP = {
    "IT·정보통신업": "10007",
    "미디어·광고업": "10005",
    "금융·은행업": "10002",
    "건설업": "10003",
    "문화·예술·디자인업": "10006"
}

# js로 클릭 버튼 유틸 함수
def click(wd, element):
    wd.execute_script("arguments[0].click();", element)

# 1단계 잡코리아 탭 클릭
def open_jobkorea_tab(wd):
    tabs = wd.find_elements(By.CSS_SELECTOR, "ul.tab-button-wrap li")
    for tab in tabs:
        if "잡코리아" in tab.text:
            click(wd, tab)
            time.sleep(2)
            return

# 2단계 카테고리 드롭다운 클릭
def open_category_dropdown(wd):
    dropdowns = wd.find_elements(By.CSS_SELECTOR, "div.dropdown-btn-wrap")

    for dropdown in dropdowns:
        span = dropdown.find_element(By.TAG_NAME, "span")
        if span.text.strip() == "희망업종":
            wd.execute_script("arguments[0].click();", dropdown)
            time.sleep(1)
            return

# 3단계 카테고리 선택
def select_category(wd, category_name):
    target_value = TARGET_CATEGORIES_MAP[category_name]

    labels = wd.find_elements(By.CSS_SELECTOR, "div.dropdown-content-wrap.isOpen label")

    for label in labels:
        checkbox = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        if checkbox.get_attribute("value") == target_value:
            wd.execute_script("arguments[0].click();", label)
            time.sleep(2)
            return

# 4단계 제목 크롤링
def load_titles_from_page(wd):
    results = []

    WebDriverWait(wd, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.tab-content.active tbody.post-list-body tr.post-td")))

    rows = wd.find_elements(By.CSS_SELECTOR, "div.tab-content.active tbody.post-list-body tr.post-td")

    for row in rows[:10]:
        title_td = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")

        raw_text = wd.execute_script("return arguments[0].textContent;",title_td)
        title = " ".join(raw_text.split()).strip()

        if title:
            results.append(title)

    return results

# 5단계 다음 버튼 클릭
def click_next_page(wd):
    spans = wd.find_elements(By.CSS_SELECTOR, "div.pager-wrap span")
    for span in spans:
        if span.text.strip() == ">":
            click(wd, span)
            return True
        
    return False

# 6단계 카테고리 초기화
def reset(wd):
    close_btn = wd.find_element(By.CSS_SELECTOR, "div.search-bar-bottom-tag-list-wrap div.tag div.tag__text span")
    wd.execute_script("arguments[0].click();", close_btn)
    time.sleep(1)

def jobkorea_recruitment_info_crawling():
    wd = webdriver.Chrome()
    wd.get("https://job.skuniv.ac.kr/recruit-external/")
    time.sleep(2)

    # 1단계 잡코리아 탭 클릭
    open_jobkorea_tab(wd)

    all_titles = []

    # 2단계 카테고리 드롭다운 클릭
    open_category_dropdown(wd)

    for category in TARGET_CATEGORIES_MAP:
        print(f"[업종] {category} 크롤링 시작")

        # 3단계 카테고리 선택
        select_category(wd, category)
        time.sleep(2)

        page = 1
        while page <= MAX_PAGES:
            print(f"- {page} 페이지 크롤링 중")
            
            # 4단계 제목 크롤링
            titles = load_titles_from_page(wd)
            all_titles.extend(titles)

            # 7단계 크롤링 종료(MAX_TITLES만큼 수집 시)
            if len(all_titles) >= MAX_TITLES:
                wd.quit()
                return all_titles[:MAX_TITLES]

            # 5단계 다음 버튼 클릭
            if not click_next_page(wd):
                break

            time.sleep(2.5)
            page += 1

        # 6단계 카테고리 초기화
        reset(wd)

    wd.quit()
    return all_titles

titles = jobkorea_recruitment_info_crawling()
df = pd.DataFrame({"title": titles})
df.to_csv("../recruitment_info_analysis/jobkorea_recruitment_titles.csv", index=False, encoding="utf-8-sig")

print(f"크롤링된 잡코리아 채용 정보 글 개수: {len(df)}")
print("jobkorea_recruitment_titles.csv 저장 완료")