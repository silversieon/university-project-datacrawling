from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_post_links(wd):
    html = wd.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    links = []
    tbody = soup.select_one("tbody.post-list-body")
    if not tbody:
        return links
    
    rows = tbody.select("tr.post-td")
    
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 2:
            continue
        
        title_td = tds[1]
        link_element = title_td.find("a")
        
        if link_element and link_element.get("href"):
            href = link_element.get("href")
            if not href.startswith("http"):
                href = "https://job.skuniv.ac.kr" + href
            
            number = tds[0].get_text(strip=True)
            title = title_td.get_text(strip=True)
            
            links.append({
                "number": number,
                "title": title,
                "url": href
            })
    
    return links

def get_post_content(wd, url):
    try:
        wd.get(url)
        time.sleep(0.5)
        
        html = wd.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # editor-wrap 클래스만 선택
        content_area = soup.select_one("div.editor-wrap")
        
        if content_area:
            # 이미지 태그 제거
            for img in content_area.find_all("img"):
                img.decompose()
            
            # 텍스트만 추출
            content = content_area.get_text(separator="\n", strip=True)
            return content
        else:
            return "내용을 찾을 수 없음"
            
    except Exception as e:
        print(f"Error getting content from {url}: {str(e)}")
        return f"크롤링 실패: {str(e)}"

def click_next_page(wd):
    try:
        spans = wd.find_elements(By.CSS_SELECTOR, "div.pager-wrap span")
        
        for span in spans:
            if span.text.strip() == ">":
                wd.execute_script("arguments[0].click();", span)
                return True
        
        return False
    except:
        return False

def skuniv_recruitment_body_crawling():
    wd = webdriver.Chrome()
    wd.get("https://job.skuniv.ac.kr/recruit-skuniv/")
    time.sleep(1.5)  
    
    all_results = []
    page = 1
    
    while True:
        print(f"교내 채용 정보 {page}페이지 크롤링 중...")
        
        # 현재 페이지의 게시글 링크 수집
        post_links = get_post_links(wd)
        print(f"  - {len(post_links)}개의 게시글 발견")
        
        for idx, post in enumerate(post_links, 1):
            print(f"  - [{idx}/{len(post_links)}] 게시글 본문 크롤링 중: {post['title'][:30]}...")
            
            content = get_post_content(wd, post['url'])
            
            all_results.append({
                "number": post['number'],
                "title": post['title'],
                "content": content,
                "url": post['url']
            })
            
            wd.back()
            time.sleep(0.3)  
        
        if not click_next_page(wd):
            print("마지막 페이지에 도달하여 크롤링을 종료합니다.")
            break
        
        time.sleep(0.7)  
        page += 1
    
    wd.quit()
    return all_results

if __name__ == "__main__":
    print("교내 채용 정보 본문 크롤링을 시작합니다...")
    
    results = skuniv_recruitment_body_crawling()
    
    df = pd.DataFrame(results)
    output_file = "skuniv_recruitment_body.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    
    print(f"\n크롤링 완료!")
    print(f"총 {len(df)}개의 게시글 수집")
    print(f"저장 파일: {output_file}")
