import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(
    page_title="데이터 크롤링 기말 프로젝트 1",
    layout="wide"
)

# API 서버 주소 설정
API_BASE_URL = "http://127.0.0.1:8000"

def show_image_from_path(path, caption):
    if os.path.exists(path):
        st.image(path, caption=caption, use_container_width=True)
    else:
        st.warning(f"이미지를 찾을 수 없습니다: `{path}`")

# API 호출 함수
def call_api(endpoint):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API 서버 오류 (Status: {response.status_code})")
            return None
    except requests.exceptions.ConnectionError:
        st.error("API 서버에 연결할 수 없습니다.")
        return None

# 사이드바 메뉴
st.sidebar.title("Analysis Dashboard")
menu = st.sidebar.radio(
    "분석 단계",
    ["1. 프로젝트 개요", 
     "2. 원인 분석 (기기/플랫폼)", 
     "3. 현황 분석 (범죄유형)", 
     "4. 심층 분석 (연령/피해액)", 
     "5. 지역 분석 (지도)",
     "6. [API] 연령별 위험도",
     "7. [API] 지역별 위험도"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Client-Server Architecture Ver.")

# 메인 페이지
if menu == "1. 프로젝트 개요":
    st.title("디지털 시대로 인한 사이버 금융 범죄 문제")
    st.markdown("주제: 데이터 기반 범죄 분석 및 위험도 예측 시스템")
    st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b", caption="Digital Financial Crime", use_container_width=True)

elif menu == "2. 원인 분석 (기기/플랫폼)":
    st.title("원인 분석: 모바일로의 대이동")
    show_image_from_path("API/internet_banking_usage/internet_banking_usage.png", "인터넷 뱅킹 이용 수단 변화")

elif menu == "3. 현황 분석 (범죄유형)":
    st.title("현황 분석: 기술형에서 심리형으로")
    show_image_from_path("API/cyber_crime_analysis/cyber_crime_analysis.png", "범죄 유형별 발생 추이")

elif menu == "4. 심층 분석 (연령/피해액)":
    st.title("심층 분석: 피해자 프로파일링")
    t1, t2, t3, t4 = st.tabs(["연령별", "유형별", "피해규모", "활동연관성"])
    with t1: show_image_from_path("API/age_voice_phising/age_voice_phishing_visualization.png", "연령별 피해 추이")
    with t2: show_image_from_path("API/cyber_crime_deep_analysis/property_crime_visualization.png", "재산 범죄 유형")
    with t3: show_image_from_path("API/cyber_crime_deep_analysis/fraud_damage_visualization.png", "피해 유형 분석")
    with t4: show_image_from_path("API/cyber_crime_deep_analysis/online_activity_visualization.png", "온라인 활동 연관성")

elif menu == "5. 지역 분석 (지도)":
    st.title("지역별 분석: 범죄의 핫스팟")
    show_image_from_path("API/regional_voice_phishing/regional_voice_phishing_visualization.png", "지역별 피해 히트맵")

elif menu == "6. [API] 연령별 위험도":
    st.title("실시간 API 연동 테스트: 연령별 위험도")    
    if st.button("API 요청 보내기 (GET)"):
        with st.spinner():
            json_data = call_api("/api/ageStatistics")
            
            if json_data:
                st.success("서버 응답 수신 완료")
                
                df = pd.DataFrame.from_dict(json_data, orient="index")
                st.dataframe(df.style.applymap(
                    lambda x: "color: red; font-weight: bold" if x == "HIGH" else 
                              ("color: orange" if x == "MID" else "color: green"),
                    subset=["isHazard"]
                ), use_container_width=True)
                
                with st.expander("원본 JSON 데이터 보기"):
                    st.json(json_data)

elif menu == "7. [API] 지역별 위험도":
    st.title("실시간 API 연동 테스트: 지역별 위험도")
    
    if st.button("API 요청 보내기 (GET)"):
        with st.spinner():
            json_data = call_api("/api/regionalStatistics")
            
            if json_data:
                st.success("서버 응답 수신 완료")
                
                df = pd.DataFrame.from_dict(json_data, orient="index")
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.dataframe(df.style.applymap(
                        lambda x: "background-color: #ffcccc" if x == "VERY_HIGH" else "",
                        subset=["isHazard"]
                    ), use_container_width=True)
                with c2:
                    st.write("**위험 지역 목록**")
                    high_risk = df[df["isHazard"].isin(["HIGH", "VERY_HIGH"])]
                    st.table(high_risk[["isHazard"]])

                with st.expander("원본 JSON 데이터 보기"):
                    st.json(json_data)