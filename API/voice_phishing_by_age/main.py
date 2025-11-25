import os
import platform
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# 경찰청_전화금융사기 피해자 연령별 현황 

load_dotenv()
service_key = os.getenv("API_SERVICE_KEY") 

base_url = "https://api.odcloud.kr/api"
endpoint = "/15091221/v1/uddi:e359f7f2-b59c-402f-9818-8d027df1a426"
request_url = base_url + endpoint

# 데이터 수집 
def fetch_data():
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
        
        if 'data' in data:
            df = pd.DataFrame(data['data'])
            if '구분' in df.columns:
                df = df.rename(columns={'구분': '연도'})
                df = df.sort_values(by='연도') 
            return df
        else:
            return None

    except Exception as e:
        print(f"API 요청 실패: {e}")
        return None

# 시각화
def visualize_dashboard(df):

    system_name = platform.system()
    if system_name == 'Darwin': 
        plt.rc('font', family='AppleGothic')
    elif system_name == 'Windows': 
        plt.rc('font', family='Malgun Gothic')
    else: 
        plt.rc('font', family='NanumGothic')
    plt.rc('axes', unicode_minus=False)

    # 데이터 구조 변환 (Wide -> Long Format)
    age_cols = [col for col in df.columns if '대' in col]
    df_melted = df.melt(id_vars=['연도'], value_vars=age_cols, 
                        var_name='연령대', value_name='피해건수')
    
    age_order = sorted(age_cols) 

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    sns.lineplot(data=df_melted, x='연도', y='피해건수', hue='연령대', hue_order=age_order,
                 marker='o', linewidth=2.5, ax=axes[0], palette='tab10')
    
    axes[0].set_title('연도별 보이스피싱 피해 발생 추이 (연령대별)', fontsize=15, pad=15)
    axes[0].set_ylabel('피해 발생 건수')
    axes[0].grid(True, linestyle='--', alpha=0.6)
    
    # 주요 지점 값 표시 (최신 연도 기준)
    latest_year = df['연도'].max()
    latest_data = df_melted[df_melted['연도'] == latest_year]
    for _, row in latest_data.iterrows():
        axes[0].text(row['연도'], row['피해건수'], f"{row['피해건수']:,}", 
                     fontsize=9, ha='left', va='center', fontweight='bold')

    df_pivot = df.set_index('연도')[age_cols]
    
    # 백분율(%)로 변환하여 상대적 비중 비교
    df_pct = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    df_pct.plot(kind='bar', stacked=True, ax=axes[1], colormap='tab10', width=0.7)
    
    axes[1].set_title('연도별 피해자 연령대 비중 변화 (%)', fontsize=15, pad=15)
    axes[1].set_ylabel('비중 (%)')
    axes[1].legend(title='연령대', bbox_to_anchor=(1.05, 1), loc='upper left')
    axes[1].grid(axis='y', linestyle='--', alpha=0.4)
    plt.xticks(rotation=0)

    # 그래프 값 표시
    for c in axes[1].containers:
        labels = [f'{v.get_height():.1f}%' if v.get_height() > 5 else '' for v in c]
        axes[1].bar_label(c, labels=labels, label_type='center', fontsize=9, color='white', fontweight='bold')

    plt.tight_layout()
    
    save_name = 'voice_phishing_age_analysis.png'
    plt.savefig(save_name, dpi=300)
    print(f"그래프 저장 완료: {save_name}")
    plt.show()

# 메인 
if __name__ == "__main__":
    df = fetch_data()
    
    if df is not None:
        print("\n[데이터 미리보기]")
        print(df.head())
        
        visualize_dashboard(df)