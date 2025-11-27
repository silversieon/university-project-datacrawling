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

def request_regional_api():
    params = {
        "page": 1,
        "perPage": 100,
        "returnType": "json",
        "serviceKey": service_key
    }
    try:
        response = requests.get(request_url, params=params)

        data = response.json()
        if "data" in data:
            data_frame = pd.DataFrame(data["data"])
            return data_frame
        else:
            return None

    except Exception as e:
        return None

def visualize_regional_voice_phishing(data):
    
    # 폰트 설정(안 해주면 글씨가 깨져서 임의로 지정했습니다)
    system = platform.system()
    if system == "Darwin": plt.rc("font", family="AppleGothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)

    # data.to_csv("C:/develop/datacrawling/regional_voice_phishing_data.csv", index=False, encoding="utf-8-sig")
    
    # "시도청"을 기준 인덱스로 설정
    if "시도청" in data.columns:
        data = data.set_index("시도청")

    # 컬럼명에서 "년" 제거 후 정수형 변환(년도 숫자만 남기기)
    data.columns = [int(c.replace("년", "")) for c in data.columns]

    # data.to_csv("C:/develop/datacrawling/regional_voice_phishing_data.csv", index=True, encoding="utf-8-sig")

    # [그래프 그리기] 지역별/연도별 히트맵
    sns.heatmap(data, annot=True, fmt="d", cmap="Blues", linewidths=.10, linecolor="lightgray")
    plt.title('지역별 보이스피싱 피해 통계 히트맵', fontsize=18)
    
    # 시각화 자료 저장
    save_name = "regional_voice_phishing_visualization.png"
    plt.savefig(save_name, dpi=300)
    print(f"지역별/연도별 시각화 히트맵 저장 완료: {save_name}")

def regional_voice_phishing():
    data = request_regional_api()
    
    if data is not None:
        visualize_regional_voice_phishing(data)
    else:
        print("지역별/연도별 보이스피싱 통계 데이터를 불러오지 못했습니다.")