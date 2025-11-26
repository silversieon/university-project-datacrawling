import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 사기 피해 중 보이스피싱 비율(한국형사법무정책연구원_전국범죄피해조사정보조회서비스)

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY")

base_url = "http://apis.data.go.kr/B554626/NationalCrimeVictimInvestigation"
endpoint = "/getNationalCrimeVictimInvestigation"
request_url = base_url + endpoint

def request_fraud_damage_api():
    params = {
        "serviceKey": service_key,
        "type": "json",
        "sht": "T232483026149933",
        "statsYr": "2020",
    }
    try:
        response = requests.get(request_url, params=params)
        
        data = response.json()
        data = data["response"]["body"]["items"]["item"]
        artcl = data["artcl"]
        stats = data["statsVl"][0]
        
        data_frame = pd.DataFrame(artcl, columns=["종류", "비율"])
        data_frame["비율"] = stats
        return data_frame

    except Exception as e:
        return None

def visualize_fraud_damage(data):
    # 폰트 설정(안 해주면 글씨가 깨져서 임의로 지정했습니다)
    system = platform.system()
    if system == "Darwin": plt.rc("font", family="AppleGothic")
    else: plt.rc("font", family="NanumGothic")
    plt.rc("axes", unicode_minus=False)

    # data.to_csv("C:/develop/datacrawling/visualize_fraud_damage_data.csv", index=False, encoding="utf-8-sig")
    
    # 사기 피해 유형명 변경(너무 길어서 축약해서 표시했습니다!)
    replace_dict = {
        "돈을 갚을 의사나 능력이 없으면서 갚겠다고 속여 돈을 빌려 가서 못받음": "빌리고 안갚음",
        "전화로 은행, 카드회사, 국세청, 경찰, 검찰 등을 사칭하여 돈이나 개인정보를 요구함": "피싱1(사칭)",
        "전화로 자녀를 납치했다고 하면서 돈을 요구함(보이스 피싱 등)": "피싱2(납치협박)",
        "중고거래사이트나 인터넷쇼핑몰에서 송금을 하였으나 물건을 받지 못함": "인터넷사기",
        "가짜 상품을 진품이라고 속여 판매함": "사기판매",
        "주식, 분양, 사업 등 속아서 돈을 투자했다가 돌려받지 못함": "투자사기",
        "계모임 회원 중 누군가 돈을 갖고 사라짐": "계모임사기",
        "공짜, 할인, 경품 당첨 등을 미끼로 상품을 구매하게 함": "기타사기1",
        "그 외의 사기(속임수)로 인한 재산상의 피해": "기타사기2"
    }
    data["종류"] = data["종류"].replace(replace_dict)
    colors = ["red" if "피싱" in kind else "steelblue" for kind in data["종류"]]
    
    # [그래프 그리기] 사기 피해 유병별 비율 바차트(보이스피싱 비율 확인)
    
    plt.figure(figsize=(10,6))
    plt.bar(data["종류"], data["비율"], color=colors)
    plt.title("사기 피해 유형별 비율(보이스 피싱 비율 확인)", fontsize=20)
    plt.xlabel("사기 피해 유형")
    plt.ylabel("비율(%)")
    for _, row in data.iterrows():
        plt.text(row["종류"], row["비율"], f"{row['비율']:.1f}%", 
                    fontsize=10, ha='center', va='bottom')
    plt.grid(axis='y', alpha=0.5)
    
    # 시각화 자료 저장
    save_name = "fraud_damage_visualization.png"
    plt.savefig(save_name, dpi=300)
    print(f"사기 피해 유형 중 보이스피싱 비율 확인 지표 저장 완료: {save_name}")

def fraud_damage():
    data = request_fraud_damage_api()
    if data is not None:
        visualize_fraud_damage(data)
    else:
        print("사기 피해 종류 및 비율 데이터를 불러오지 못했습니다.")