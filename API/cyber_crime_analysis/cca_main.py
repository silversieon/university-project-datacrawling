import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# 경찰청_연도별 사이버 범죄 통계 현황

# 환경 변수 및 설정
load_dotenv()
service_key = os.getenv("API_SERVICE_KEY")
base_url = "https://api.odcloud.kr/api"
endpoint = "/15053887/v1/uddi:4a0b64ee-fee2-42c1-802b-99c651d5260a"
request_url = base_url + endpoint

# 데이터 수집 
def fetch_cyber_crime_data():
    params = {
        "serviceKey": service_key,
        "page": 1,
        "perPage": 100,
        "returnType": "json"
    }
    
    try:
        response = requests.get(request_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data:
            df = pd.DataFrame(data["data"])
            # 연도별 정렬
            if "연도" in df.columns:
                df = df.sort_values(by="연도")
            return df
        else:
            print("데이터 없음")
            return None

    except Exception as e:
        print(f"에러 발생: {e}")
        return None

# 데이터 전처리 
def preprocess_data(df):

    # "발생건수"만 필터링
    if "구분" in df.columns:
        df = df[df["구분"] == "발생건수"].copy()
    
    # 분석에 필요한 금융범죄 관련 컬럼만 선택
    target_cols = ["연도", "사이버금융범죄_피싱", "사이버금융범죄_파밍", 
                   "사이버금융범죄_스미싱", "사이버금융범죄_메모리해킹", 
                   "사이버금융범죄_메신저이용사기", "사이버금융범죄_몸캠피싱"]
    
    valid_cols = [col for col in target_cols if col in df.columns]
    df_filtered = df[valid_cols].set_index("연도")
    
    # 데이터 타입 변환 (문자열 -> 숫자)
    df_filtered = df_filtered.apply(pd.to_numeric, errors="coerce").fillna(0)
    
    return df_filtered

# 시각화 (Visualization)
def visualize_data(df):
    
    system_name = platform.system()
    if system_name == "Darwin":
        plt.rc("font", family="AppleGothic")
    else:
        plt.rc("font", family="NanumGothic")
    
    plt.rc("axes", unicode_minus=False) # 마이너스 기호 깨짐 방지

    # 그래프 그리기
    fig, axes = plt.subplots(2, 1, figsize=(12, 12))
    
    # [그래프 1] 연도별 전체 사이버 금융범죄 발생 총합 
    df["total"] = df.sum(axis=1) # 연도별 합계 계산
    sns.lineplot(data=df, x=df.index, y="total", marker="o", ax=axes[0], color="#FF6B6B", linewidth=2.5)
    axes[0].set_title("연도별 사이버 금융범죄 발생 추이 (총합)", fontsize=15, pad=15)
    axes[0].set_ylabel("발생 건수")
    axes[0].grid(True, linestyle="--", alpha=0.6)
    
    for x, y in zip(df.index, df["total"]):
        axes[0].text(x, y + (y*0.02), f"{int(y):,}", ha="center", fontsize=10)

    # [그래프 2] 범죄 유형별 상세 비교 
    df_details = df.drop(columns=["total"])
    sns.lineplot(data=df_details, markers=True, dashes=False, ax=axes[1], linewidth=2, palette="cool")
    axes[1].set_title("유형별 사이버 금융범죄 상세 추이", fontsize=15, pad=15)
    axes[1].set_ylabel("발생 건수")
    axes[1].legend(title="범죄 유형", bbox_to_anchor=(1.05, 1), loc="upper left")
    axes[1].grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    
    # 그래프 저장 및 출력
    plt.savefig("cyber_crime_analysis.png", dpi=300)
    print("그래프 저장 완료: cyber_crime_analysis.png")
    plt.show()

# 메인
if __name__ == "__main__":
    # 데이터 수집 및 전처리
    raw_df = fetch_cyber_crime_data()
    
    if raw_df is not None:
        # 전처리
        clean_df = preprocess_data(raw_df)
        
        # 데이터 확인 (터미널 출력)
        print("\n[전처리된 데이터]")
        print(clean_df.head())
        
        # 시각화
        visualize_data(clean_df)