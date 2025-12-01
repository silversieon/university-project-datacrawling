import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# 폰트 설정
def _set_korean_font():
    system = platform.system()
    if system == "Darwin": plt.rc("font", family="AppleGothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)
    
# 데이터 수집
def _fetch_data(service_key):
    base_url = "https://api.odcloud.kr/api"
    endpoint = "/15053887/v1/uddi:4a0b64ee-fee2-42c1-802b-99c651d5260a"
    request_url = base_url + endpoint
    
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
            if "연도" in df.columns:
                df = df.sort_values(by="연도")
            return df
        else:
            print("데이터 없음")
            return None

    except Exception as e:
        print(f"API 요청 중 에러 발생: {e}")
        return None

# 3. 데이터 전처리 
def _preprocess(df):
    # "발생건수"만 필터링
    if "구분" in df.columns:
        df = df[df["구분"] == "발생건수"].copy()
    
    # 타겟 컬럼
    target_cols = ["연도", "사이버금융범죄_피싱", "사이버금융범죄_파밍", 
                   "사이버금융범죄_스미싱", "사이버금융범죄_메모리해킹", 
                   "사이버금융범죄_메신저이용사기", "사이버금융범죄_몸캠피싱"]
    
    valid_cols = [col for col in target_cols if col in df.columns]
    
    df_filtered = df[valid_cols].copy()
    
    for col in valid_cols:
        if col != "연도":
            df_filtered[col] = pd.to_numeric(df_filtered[col], errors="coerce").fillna(0)
    
    return df_filtered.set_index("연도")

# 시각화 및 저장 
def _visualize(df):
    _set_korean_font()

    fig, axes = plt.subplots(2, 1, figsize=(12, 12))
    
    # [그래프 1] 총합 추이
    df["total"] = df.sum(axis=1)
    sns.lineplot(data=df, x=df.index, y="total", marker="o", ax=axes[0], color="#FF6B6B", linewidth=2.5)
    axes[0].set_title("연도별 사이버 금융범죄 발생 추이 (총합)", fontsize=16, fontweight='bold', pad=15)
    axes[0].set_ylabel("발생 건수")
    axes[0].grid(True, linestyle="--", alpha=0.6)
    
    for x, y in zip(df.index, df["total"]):
        axes[0].text(x, y + (y*0.02), f"{int(y):,}", ha="center", fontsize=10)

    # [그래프 2] 유형별 상세 비교
    df_details = df.drop(columns=["total"])
    sns.lineplot(data=df_details, markers=True, dashes=False, ax=axes[1], linewidth=2, palette="cool")
    axes[1].set_title("유형별 상세 추이: 피싱/메신저사기 vs 기술형 범죄", fontsize=16, fontweight='bold', pad=15)
    axes[1].set_ylabel("발생 건수")
    axes[1].legend(title="범죄 유형", bbox_to_anchor=(1.05, 1), loc="upper left")
    axes[1].grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    
    # 파일 저장
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_name = "cyber_crime_analysis.png"
    save_path = os.path.join(current_dir, save_name)
    
    plt.savefig(save_path, dpi=300)
    print(f"시각화 저장 완료: {save_path}")
    # plt.show()

def cyber_crime_trend_analysis():
    load_dotenv()
    service_key = os.getenv("API_SERVICE_KEY")
    
    if not service_key:
        return

    # 데이터 수집
    raw_df = _fetch_data(service_key)
    
    if raw_df is not None:
        # 전처리
        clean_df = _preprocess(raw_df)
        
        # 시각화
        _visualize(clean_df)
    else:
        print("데이터 수집 실패로 분석을 중단합니다.")

if __name__ == "__main__":
    cyber_crime_trend_analysis()