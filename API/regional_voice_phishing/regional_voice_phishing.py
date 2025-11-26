import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# 경찰청_전화금융사기 시도경찰청별 피해 현황

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY")

base_url = "https://api.odcloud.kr/api"
endpoint = "/15091224/v1/uddi:74e5825b-ab3d-418e-9af9-c35429bcffb4"
request_url = base_url + endpoint

def fetch_regional_data():
    
    headers = {"Authorization": service_key}
    params = {
        "page": 1,
        "perPage": 100,
        "returnType": "json"
    }
    
    try:
        response = requests.get(request_url, params=params, headers=headers)
        
        if response.status_code == 401:
            params["serviceKey"] = service_key
            response = requests.get(request_url, params=params)

        response.raise_for_status()
        data = response.json()
        
        if "data" in data:
            df = pd.DataFrame(data["data"])
            return df
        else:
            return None

    except Exception as e:
        return None

def visualize_regional_voice_phishing(df):
    
    system_name = platform.system()
    if system_name == "Darwin": plt.rc("font", family="AppleGothic")
    elif system_name == "Windows": plt.rc("font", family="Malgun Gothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)

    # 전처리
    # "시도청"을 인덱스로 설정
    if "시도청" in df.columns:
        df = df.set_index("시도청")
    
    # 연도 컬럼만 추출 
    year_cols = [c for c in df.columns if "년" in c]
    df_years = df[year_cols].copy()
    
    df_years.columns = [int(c.replace("년", "")) for c in df_years.columns]
    
    # 연도순 정렬
    df_years = df_years.sort_index(axis=1)

    # 그래프 그리기
    fig, axes = plt.subplots(2, 1, figsize=(14, 14))

    # [그래프 1] 지역별/연도별 히트맵 
    sns.heatmap(df_years, annot=True, fmt="d", cmap="Reds", linewidths=.5, ax=axes[0])
    axes[0].set_title("연도별/지역별 전화금융사기 피해 건수 히트맵", fontsize=16, pad=20)
    axes[0].set_xlabel("연도")
    axes[0].set_ylabel("시도경찰청")

    # [그래프 2] 피해 상위 5개 지역 추세선 (Line Chart)
    top_5_regions = df_years.sum(axis=1).nlargest(5).index
    df_top_5 = df_years.loc[top_5_regions].T 

    sns.lineplot(data=df_top_5, markers=True, dashes=False, linewidth=3, ax=axes[1], palette="tab10")
    axes[1].set_title(f"피해 집중 상위 5개 지역 발생 추이 ({", ".join(top_5_regions)})", fontsize=16, pad=20)
    axes[1].set_ylabel("발생 건수")
    axes[1].set_xlabel("연도")
    axes[1].grid(True, linestyle="--", alpha=0.5)
    axes[1].legend(title="지역", fontsize=12)

    # 값 표시
    latest_year = df_years.columns[-1]
    for region in top_5_regions:
        val = df_years.loc[region, latest_year]
        axes[1].text(latest_year, val, f"{val:,}", ha="left", va="center", fontweight="bold")

    plt.tight_layout()
    
    save_name = "regional_voice_phishing_analysis.png"
    plt.savefig(save_name, dpi=300)
    print(f"그래프 저장 완료: {save_name}")
    plt.show()

def regional_voice_phishing():
    data = fetch_regional_data()
    
    if data is not None:
        visualize_regional_voice_phishing(data)
    else:
        print("지역별 보이스피싱 통계 데이터를 불러오지 못했습니다.")