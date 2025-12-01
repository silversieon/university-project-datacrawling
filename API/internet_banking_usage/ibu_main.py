import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform

# 폰트 설정
def set_korean_font():
    system = platform.system()
    if system == "Darwin": plt.rc("font", family="AppleGothic")
    else: plt.rc("font", family="NanumGothic")
    
    plt.rc("axes", unicode_minus=False)

# 데이터 로드 및 분리
def load_and_split_data(file_name):
    
    try:
        df = pd.read_csv(file_name, header=[0, 1])
    except FileNotFoundError:
        return None, None

    def clean_numeric(series):
        return pd.to_numeric(series.astype(str).str.replace("-", "0"), errors="coerce")

    # 스마트폰 vs 데스크탑
    df_p1 = pd.DataFrame()
    df_p1["연도"] = df[("시점", "시점")] 
    df_p1["스마트폰"] = clean_numeric(df[("인터넷뱅킹 서비스 접속시 이용기기", "스마트폰")])
    df_p1["데스크탑"] = clean_numeric(df[("인터넷뱅킹 서비스 접속시 이용기기", "데스크탑 컴퓨터")])
    
    df_p1 = df_p1[df_p1["연도"] <= 2018].copy()

    # 금융 서비스 유형 변화
    df_p2 = pd.DataFrame()
    df_p2["연도"] = df[("시점", "시점")]
    
    # 컬럼 정의
    col_netbank = ("인터넷뱅킹 송금시 주이용 서비스", "인터넷전문은행(케이뱅크 카카오뱅크) 인터넷뱅킹")
    col_fintech = ("인터넷뱅킹 송금시 주이용 서비스", "간편송금서비스(토스 카카오페이 페이코 네이버페이 등)")
    
    # 데이터 추출
    df_p2["인터넷전문은행"] = clean_numeric(df[col_netbank])
    df_p2["간편송금(핀테크)"] = clean_numeric(df[col_fintech])
    
    # 2019년부터 필터링
    df_p2 = df_p2[df_p2["연도"] >= 2019].copy()

    return df_p1, df_p2

# 시각화 
def visualize(df_p1, df_p2):
    set_korean_font()
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 14))
    
    # 스마트폰 vs 데스크탑
    df_p1_melt = df_p1.melt(id_vars=["연도"], value_vars=["스마트폰", "데스크탑"], 
                            var_name="기기", value_name="이용률")
    
    sns.lineplot(data=df_p1_melt, x="연도", y="이용률", hue="기기", style="기기", 
                 markers=True, dashes=False, ax=axes[0], linewidth=3, palette=["#FF6B6B", "#4D96FF"])
    
    axes[0].set_title("스마트폰 vs 데스크탑", fontsize=16, fontweight="bold", pad=20)
    axes[0].set_ylabel("이용률 (%)", fontsize=12)
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend(fontsize=12)

    # 금융 서비스 유형 변화 
    df_p2_melt = df_p2.melt(id_vars=["연도"], value_vars=["인터넷전문은행", "간편송금(핀테크)"], var_name="서비스", value_name="이용률")

    sns.barplot(data=df_p2_melt, x="연도", y="이용률", hue="서비스", ax=axes[1], palette="Pastel1")
    
    axes[1].set_title("금융 서비스 유형 변화", fontsize=16, fontweight="bold", pad=20)
    axes[1].set_ylabel("이용률 (%)", fontsize=12)
    axes[1].grid(True, axis="y", linestyle="--", alpha=0.5)
    axes[1].legend(title="금융 서비스 유형", fontsize=11)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15) 
    
    save_name = "internet_banking_usage.png"
    plt.savefig(save_name, dpi=300)
    print(f"그래프 저장 완료: {save_name}")
    plt.show()

# 메인
if __name__ == "__main__":
    csv_file = "인터넷뱅킹이용률및이용기기_20251124224154.csv"
    
    df_phase1, df_phase2 = load_and_split_data(csv_file)
    
    if df_phase1 is not None and df_phase2 is not None:
        visualize(df_phase1, df_phase2)