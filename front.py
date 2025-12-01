import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import platform
import requests
import numpy as np
from sklearn.cluster import KMeans
from dotenv import load_dotenv

st.set_page_config(
    page_title="사이버 금융범죄 분석 & 위험도 예측",
    layout="wide"
)

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY")

def set_korean_font():
    system_name = platform.system()
    if system_name == 'Darwin': font_family = 'AppleGothic'
    elif system_name == 'Windows': font_family = 'Malgun Gothic'
    else: font_family = 'NanumGothic'
    
    plt.rc('font', family=font_family)
    plt.rc('axes', unicode_minus=False)

set_korean_font()

# [데이터 로드 함수]
@st.cache_data
def load_banking_data():
    file_name = "인터넷뱅킹이용률및이용기기_20251124224154.csv"
    try:
        df = pd.read_csv(file_name, header=[0, 1])
        return df
    except FileNotFoundError:
        return None

@st.cache_data
def fetch_crime_trend_data():
    url = "https://api.odcloud.kr/api/15064566/v1/uddi:311fe198-a727-4bf5-8f5d-a7999483db20"
    params = {"page": 1, "perPage": 100, "returnType": "json", "serviceKey": service_key}
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            df = pd.DataFrame(res.json()['data'])
            return df.sort_values('연도') if '연도' in df.columns else df
    except: pass
    return pd.DataFrame()

@st.cache_data
def fetch_victim_age_data():
    url = "https://api.odcloud.kr/api/15091221/v1/uddi:e359f7f2-b59c-402f-9818-8d027df1a426"
    headers = {"Authorization": service_key} 
    params = {"page": 1, "perPage": 100, "returnType": "json"}
    try:
        res = requests.get(url, params=params, headers=headers)
        if res.status_code != 200:
            params['serviceKey'] = service_key
            res = requests.get(url, params=params)
        if res.status_code == 200:
            df = pd.DataFrame(res.json()['data'])
            if '구분' in df.columns:
                df = df.rename(columns={'구분': '연도'}).sort_values('연도')
            return df
    except: pass
    return pd.DataFrame()

@st.cache_data
def fetch_regional_data():
    url = "https://api.odcloud.kr/api/15091224/v1/uddi:74e5825b-ab3d-418e-9af9-c35429bcffb4"
    headers = {"Authorization": service_key}
    params = {"page": 1, "perPage": 100, "returnType": "json"}
    try:
        res = requests.get(url, params=params, headers=headers)
        if res.status_code != 200:
            params['serviceKey'] = service_key
            res = requests.get(url, params=params)
        if res.status_code == 200:
            df = pd.DataFrame(res.json()['data'])
            if '시도청' in df.columns:
                df = df.set_index('시도청')
            return df
    except: pass
    return pd.DataFrame()

# [API 로직 시뮬레이션 함수]
def calculate_age_hazard():
    data = fetch_victim_age_data()
    if data.empty: return None
    
    data = data.set_index('연도')
    age_columns = [c for c in data.columns if '대' in c] # 연령 컬럼만 추출
    data = data[age_columns]

    latest_year = data.index.max()
    pre_year = latest_year - 1
    
    # 데이터가 문자열일 경우 숫자 변환
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

    pre_grow_rate = (data.loc[latest_year] - data.loc[pre_year]) / data.loc[pre_year] * 100
    mean = data.drop(latest_year).mean()
    mean_grow_rate = (data.loc[latest_year] - mean) / mean * 100

    # NaN 처리 (0으로 나누는 경우 등)
    pre_grow_rate = pre_grow_rate.fillna(0)
    mean_grow_rate = mean_grow_rate.fillna(0)

    X = np.column_stack([pre_grow_rate.values, mean_grow_rate.values])
    
    kmeans = KMeans(n_clusters=3, random_state=0, n_init='auto')
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_
    cluster_score = np.argsort(centers.mean(axis=1))
    
    hazard_map = {cluster_score[0]: "LOW", cluster_score[1]: "MID", cluster_score[2]: "HIGH"}
    
    results = []
    for i, age in enumerate(age_columns):
        results.append({
            "연령대": age,
            "전년 대비 증가율(%)": round(pre_grow_rate[age], 2),
            "평균 대비 증가율(%)": round(mean_grow_rate[age], 2),
            "위험군 클러스터": hazard_map[labels[i]]
        })
    return pd.DataFrame(results)

def calculate_regional_hazard():
    data = fetch_regional_data()
    if data.empty: return None

    # 연도 컬럼만 추출 및 정수 변환
    year_cols = [c for c in data.columns if '년' in c]
    data = data[year_cols].copy()
    data.columns = [int(c.replace("년", "")) for c in data.columns]
    
    # 로직상 Transpose 필요 (지역이 컬럼이 되도록)
    data = data.T 
    region_columns = data.columns

    latest_year = data.index.max()
    pre_year = latest_year - 1

    pre_grow_rate = (data.loc[latest_year] - data.loc[pre_year]) / data.loc[pre_year] * 100
    mean = data.drop(latest_year).mean()
    mean_grow_rate = (data.loc[latest_year] - mean) / mean * 100

    pre_grow_rate = pre_grow_rate.fillna(0)
    mean_grow_rate = mean_grow_rate.fillna(0)

    X = np.column_stack([pre_grow_rate.values, mean_grow_rate.values])

    kmeans = KMeans(n_clusters=5, random_state=0, n_init='auto')
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_
    cluster_score = np.argsort(centers.mean(axis=1))

    hazard_map = {
        cluster_score[0]: "VERY_LOW", cluster_score[1]: "LOW", cluster_score[2]: "MID",
        cluster_score[3]: "HIGH", cluster_score[4]: "VERY_HIGH"
    }

    results = []
    for i, region in enumerate(region_columns):
        results.append({
            "지역": region,
            "전년 대비 증가율(%)": round(pre_grow_rate[region], 2),
            "평균 대비 증가율(%)": round(mean_grow_rate[region], 2),
            "위험군 클러스터": hazard_map[labels[i]]
        })
    return pd.DataFrame(results)

# [사이드바 메뉴]
st.sidebar.title("🕵️‍♂️ Analysis Dashboard")
menu = st.sidebar.radio(
    "메뉴 선택",
    ["1. 프로젝트 개요", 
     "2. 원인 분석 (기기/플랫폼)", 
     "3. 현황 분석 (범죄유형)", 
     "4. 심층 분석 (연령/피해액)", 
     "5. 지역 분석 (지도)",
     "6. [API 테스트] 연령별 위험도",
     "7. [API 테스트] 지역별 위험도"]
)

# ==========================================
# [메인 로직]
# ==========================================

if menu == "1. 프로젝트 개요":
    st.title("사이버 금융범죄 분석 프로젝트")
    st.image("https://images.unsplash.com/photo-1550751827-4bd374c3f58b", caption="Cyber Security")
    st.info("이 대시보드는 금융범죄의 원인부터 현황, 그리고 머신러닝(K-Means)을 이용한 위험도 예측 모델까지 통합적으로 보여줍니다.")

elif menu == "2. 원인 분석 (기기/플랫폼)":
    st.title("기기와 플랫폼의 변화")
    df = load_banking_data()
    if df is not None:
        def clean_numeric(s): return pd.to_numeric(s.astype(str).str.replace('-', '0'), errors='coerce')
        
        tab1, tab2 = st.tabs(["기기 변화 (Phase 1)", "플랫폼 변화 (Phase 2)"])
        
        with tab1:
            df_p1 = pd.DataFrame()
            df_p1['연도'] = df[('시점', '시점')]
            df_p1['스마트폰'] = clean_numeric(df[('인터넷뱅킹 서비스 접속시 이용기기', '스마트폰')])
            df_p1['데스크탑'] = clean_numeric(df[('인터넷뱅킹 서비스 접속시 이용기기', '데스크탑 컴퓨터')])
            df_p1 = df_p1[df_p1['연도'] <= 2018]
            
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.lineplot(data=df_p1.melt('연도'), x='연도', y='value', hue='variable', marker='o', ax=ax)
            st.pyplot(fig)
            
        with tab2:
            df_p2 = pd.DataFrame()
            df_p2['연도'] = df[('시점', '시점')]
            df_p2['인터넷전문은행'] = clean_numeric(df[('인터넷뱅킹 송금시 주이용 서비스', '인터넷전문은행(케이뱅크 카카오뱅크) 인터넷뱅킹')])
            df_p2['핀테크'] = clean_numeric(df[('인터넷뱅킹 송금시 주이용 서비스', '간편송금서비스(토스 카카오페이 페이코 네이버페이 등)')])
            df_p2 = df_p2[df_p2['연도'] >= 2019]
            
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=df_p2.melt('연도'), x='연도', y='value', hue='variable', ax=ax)
            st.pyplot(fig)

elif menu == "3. 현황 분석 (범죄유형)":
    st.title("📉 범죄 유형 트렌드")
    df = fetch_crime_trend_data()
    if not df.empty:
        df = df[df['구분'] == '발생건수']
        cols = [c for c in ['피싱', '파밍', '메모리해킹', '메신저이용사기'] if c in df.columns]
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df.melt('연도', value_vars=cols), x='연도', y='value', hue='variable', marker='o', ax=ax)
        st.pyplot(fig)

elif menu == "4. 심층 분석 (연령/피해액)":
    st.title("연령별 피해 및 피해액 분석")
    df = fetch_victim_age_data()
    if not df.empty:
        cols = [c for c in df.columns if '대' in c]
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df.melt('연도', value_vars=cols), x='연도', y='value', hue='variable', ax=ax)
        st.pyplot(fig)

elif menu == "5. 지역 분석 (지도)":
    st.title("지역별 피해 히트맵")
    df = fetch_regional_data()
    if not df.empty:
        year_cols = [c for c in df.columns if '년' in c]
        df = df[year_cols]
        df.columns = [int(c.replace('년', '')) for c in df.columns]
        df = df.sort_index(axis=1)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(df, cmap='Reds', annot=True, fmt='d', ax=ax)
        st.pyplot(fig)

# --- API 테스트 섹션 ---
elif menu == "6. [API 테스트] 연령별 위험도":
    st.title("🧪 연령별 위험도 분석 (K-Means)")
    st.markdown("`age_statistics_api.py`의 로직을 실시간으로 실행한 결과입니다.")
    
    if st.button("분석 실행 (Run API Logic)"):
        with st.spinner("데이터 분석 중..."):
            result_df = calculate_age_hazard()
            if result_df is not None:
                st.success("분석 완료!")
                
                # 1. 결과 테이블
                st.dataframe(result_df.style.applymap(
                    lambda x: 'color: red; font-weight: bold' if x == 'HIGH' else 
                              ('color: orange' if x == 'MID' else 'color: green'),
                    subset=['위험군 클러스터']
                ))
                
                # 2. JSON 형태 미리보기
                st.subheader("API Response (JSON Format)")
                json_result = result_df.set_index('연령대').T.to_dict()
                st.json(json_result)
            else:
                st.error("데이터 로드 실패")

elif menu == "7. [API 테스트] 지역별 위험도":
    st.title("지역별 위험도 분석 (K-Means)")
    st.markdown("`regional_statistics_api.py`의 로직을 실시간으로 실행한 결과입니다.")
    
    if st.button("분석 실행 (Run API Logic)"):
        with st.spinner("지역 데이터 분석 중..."):
            result_df = calculate_regional_hazard()
            if result_df is not None:
                st.success("분석 완료!")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("위험도 평가 결과")
                    st.dataframe(result_df.style.applymap(
                        lambda x: 'background-color: #ffcccc' if x == 'VERY_HIGH' else '',
                        subset=['위험군 클러스터']
                    ))
                
                with col2:
                    st.subheader("위험 지역 Top 5")
                    high_risk = result_df[result_df['위험군 클러스터'].isin(['HIGH', 'VERY_HIGH'])]
                    st.table(high_risk[['지역', '위험군 클러스터']])
                
                st.subheader("API Response (JSON Format)")
                json_result = result_df.set_index('지역').T.to_dict()
                st.json(json_result)
            else:
                st.error("데이터 로드 실패")
