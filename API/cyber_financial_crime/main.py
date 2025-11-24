import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY")

base_url = "https://api.odcloud.kr/api"
endpoint = "/15064566/v1/uddi:311fe198-a727-4bf5-8f5d-a7999483db20"
request_url = base_url + endpoint

# 데이터 수집
def fetch_crime_data():
    headers = {"Authorization": service_key}
    params = {"page": 1, "perPage": 100, "returnType": "json"}

    try:
        response = requests.get(request_url, params=params, headers=headers)
        if response.status_code == 401:
            params["serviceKey"] = service_key
            response = requests.get(request_url, params=params)

        response.raise_for_status()
        data = response.json()
        
        if "data" in data:
            df = pd.DataFrame(data["data"])
            if "연도" in df.columns:
                df = df.sort_values(by="연도")
            return df
        return None

    except Exception as e:
        print(f"에러 발생: {e}")
        return None

# 시각화 
def visualize_single_trend(df):
    system_name = platform.system()
    if system_name == "Darwin": plt.rc("font", family="AppleGothic")
    elif system_name == "Windows": plt.rc("font", family="Malgun Gothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)

    # 전처리
    if "구분" in df.columns:
        df = df[df["구분"] == "발생건수"].copy()
    
    target_cols = ["피싱", "파밍", "메모리해킹", "메신저이용사기"]
    valid_cols = [c for c in target_cols if c in df.columns]
    
    df_melted = df.melt(id_vars=["연도"], value_vars=valid_cols, 
                        var_name="범죄유형", value_name="발생건수")

    # 그래프 그리기 
    plt.figure(figsize=(12, 7))
    
    sns.lineplot(data=df_melted, x="연도", y="발생건수", hue="범죄유형", style="범죄유형",
                 markers=True, dashes=False, linewidth=3, palette="tab10", markersize=9)
    
    plt.title("주요 사이버 금융범죄 유형별 발생 추이", fontsize=18, pad=20)
    plt.ylabel("발생 건수", fontsize=12)
    plt.xlabel("연도", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(title="범죄 유형", fontsize=11, loc="upper left")

    for i in range(df_melted.shape[0]):
        row = df_melted.iloc[i]
        if row["발생건수"] > 100: 
            plt.text(row["연도"], row["발생건수"] + 500, f"{int(row["발생건수"]):,}", 
                     ha="center", va="bottom", fontsize=9, color="black")

    plt.tight_layout()
    
    save_name = "cyber_crime_trend.png"
    plt.savefig(save_name, dpi=300)
    print(f"그래프 저장 완료: {save_name}")
    plt.show()

# 메인
if __name__ == "__main__":
    df = fetch_crime_data()
    if df is not None:
        visualize_single_trend(df)