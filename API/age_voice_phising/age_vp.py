import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# 경찰청_전화금융사기 피해자 연령별 피해 현황 

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY") 

base_url = "https://api.odcloud.kr/api"
endpoint = "/15091221/v1/uddi:e359f7f2-b59c-402f-9818-8d027df1a426"
request_url = base_url + endpoint

def request_age_api():
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
            data_frame = pd.DataFrame(data['data'])
            return data_frame
        else:
            return None

    except Exception as e:
        return None

# 시각화
def visualize_age_voice_phishing(data):

    # 폰트 설정(안 해주면 글씨가 깨져서 임의로 지정했습니다)
    system = platform.system()
    if system == "Darwin": plt.rc("font", family="AppleGothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)

    # 연도별 구분 -> 연도로 컬럼명 변경
    data = data.rename(columns={'구분': '연도'})
    # data.to_csv("C:/develop/datacrawling/age_voice_phishing_data.csv", index=False, encoding="utf-8-sig")

    # 데이터 구조 변환 (라인차트 그리기용)
    age_cols = [col for col in data.columns if '대' in col]
    data = data.melt(id_vars=['연도'], value_vars=age_cols, 
                        var_name='연령대', value_name='피해건수')
    # data.to_csv("C:/develop/datacrawling/age_voice_phishing_data_melt.csv", index=False, encoding="utf-8-sig")
    
    # [그래프 그리기] 연령대별/연도별 라인차트
    sns.lineplot(data, x='연도', y='피해건수', hue='연령대',
                marker='o', linewidth=2.0, palette='tab10')
    
    plt.title('연령대별 보이스피싱 피해 발생 추이 (연도별)', fontsize=18, pad=15)
    plt.ylabel('피해 발생 건수 (건)')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # 주요 지점 값 표시 (최신 연도만, 각 행에 대해 피해건수만 뽑아내서 표시)
    latest_year = data['연도'].max()
    latest_year_data = data[data['연도'] == latest_year]
    for _, row in latest_year_data.iterrows():
        plt.text(row['연도'], row['피해건수'], f"{row['피해건수']:,}", 
                    fontsize=10, va='center')
    
    # 시각화 자료 저장
    current_dir = os.path.dirname(os.path.abspath(__file__))

    save_name = 'age_voice_phishing_visualization.png'
    save_path = os.path.join(current_dir, save_name)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"연령대별/연도별 시각화 라인차트 저장 완료: {save_path}")

def age_voice_phishing():
    data = request_age_api()
    
    if data is not None:
        visualize_age_voice_phishing(data)
    else:
        print("연령별 보이스피싱 통계 데이터를 불러오지 못했습니다.")