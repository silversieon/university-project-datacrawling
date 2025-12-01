import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 온라인 활동 빈도와 재산범죄피해 비율의 관계(한국형사법무정책연구원_전국범죄피해조사정보조회서비스)

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY")

base_url = "http://apis.data.go.kr/B554626/NationalCrimeVictimInvestigation"
endpoint = "/getNationalCrimeVictimInvestigation"
request_url = base_url + endpoint

def request_online_activity_api():
    params = {
        "serviceKey": service_key,
        "type": "json",
        "sht": "T234763026209919",
        "statsYr": "2020",
    }
    try:
        response = requests.get(request_url, params=params)
        
        data = response.json()
        data = data["response"]["body"]["items"]["item"]
        artcl = data["artcl"]
        clsf = data["clsf"]
        stats = data["statsVl"]
        
        data_frame = []
        # 해당 온라인 활동을 자주 하는 경우의 재산 범죄 피해 비율 추출
        for i, (category, frequency) in enumerate(clsf):
            if frequency == "자주 함" or frequency == "자주하지 않음":
                value = stats[i][0]
                data_frame.append({"활동": category, "피해비율": value})
        
        data_frame = pd.DataFrame(data_frame)
        return data_frame

    except Exception as e:
        return None

def visualize_online_activity(data):
    # 폰트 설정(안 해주면 글씨가 깨져서 임의로 지정했습니다)
    system = platform.system()
    if system == "Darwin": plt.rc("font", family="AppleGothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)
    # data.to_csv("C:/develop/datacrawling/visualize_online_activity_data.csv", index=False, encoding="utf-8-sig")
    colors = ["red" if "인터넷 뱅킹" in kind else "steelblue" for kind in data["활동"]]

    # [그래프 그리기] 각 온라인 활동 빈도별 자주 하는 경우 재산 범죄 피해 비율 관계 바차트(인터넷 뱅킹 비율 확인)
    plt.figure(figsize=(10,6))
    plt.bar(data["활동"], data["피해비율"], color=colors)
    plt.title("각 온라인 활동을 자주하는 경우 재산범죄 피해 비율", fontsize=20)
    plt.xlabel("온라인 활동 유형(자주 하는 경우)")
    plt.ylabel("피해비율(%)")
    plt.grid(axis='y', alpha=0.5)
    
    # 시각화 자료 저장
    save_name = "online_activity_visualization.png"
    plt.savefig(save_name, dpi=300)
    print(f"사기 피해 유형 중 보이스피싱 비율 확인 지표 저장 완료: {save_name}")

def online_activity():
    data = request_online_activity_api()
    if data is not None:
        visualize_online_activity(data)
    else:
        print("온라인 활동 빈도와 재산 범죄 피해 비율 관계 데이터를 불러오지 못했습니다.")