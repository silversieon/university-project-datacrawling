import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 재산 범죄 중 사기 피해 비율(한국형사법무정책연구원_전국범죄피해조사정보조회서비스)

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY")

base_url = "http://apis.data.go.kr/B554626/NationalCrimeVictimInvestigation"
endpoint = "/getNationalCrimeVictimInvestigation"
request_url = base_url + endpoint

def request_property_crime_api():
    params = {
        "serviceKey": service_key,
        "type": "json",
        "sht": "A_20200924_00004",
        "statsYr": "2020",
    }
    try:
        response = requests.get(request_url, params=params)
        
        data = response.json()
        data = data["response"]["body"]["items"]["item"]
        artcl = data["artcl"]
        stats = data["statsVl"][0]
        
        data_frame = pd.DataFrame(artcl, columns=["범죄명", "지표명", "단위"])
        data_frame["값"] = stats
        return data_frame

    except Exception as e:
        return None

def visualize_property_crime(data):
    
    # 폰트 설정(안 해주면 글씨가 깨져서 임의로 지정했습니다)
    system = platform.system()
    if system == "Darwin": plt.rc("font", family="AppleGothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)

    # data.to_csv("C:/develop/datacrawling/visualize_property_crime_data.csv", index=False, encoding="utf-8-sig")
    data = data[data["지표명"] == "범죄피해건수(추정)"]
    colors = ["red" if "사기" in kind else "steelblue" for kind in data["범죄명"]]

    # [그래프 그리기] 범죄 유형별 피해건수(추정) 바차트
    plt.figure(figsize=(10,6))
    plt.bar(data["범죄명"], data["값"], color=colors)
    plt.title("재산 범죄 유형별 피해건수(추정)", fontsize=20)
    plt.ylabel("피해건수")
    for _, row in data.iterrows():
        value = int(row["값"])
        plt.text(row["범죄명"], row["값"], f"{value:,}", 
                    fontsize=10, ha='center', va='bottom')
    plt.grid(axis='y', alpha=0.5)
    
    # 시각화 자료 저장
    current_dir = os.path.dirname(os.path.abspath(__file__))

    save_name = "property_crime_visualization.png"
    save_path = os.path.join(current_dir, save_name)
    plt.savefig(save_path, dpi=300)
    print(f"재산범죄 중 사기 피해 비율 확인 지표 저장 완료: {save_path}")
    
def property_crime():
    data = request_property_crime_api()
    if data is not None:
        visualize_property_crime(data)
    else:
        print("재산 범죄 중 사기 피해 비율 데이터를 불러오지 못했습니다.")