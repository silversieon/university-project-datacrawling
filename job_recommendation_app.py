import streamlit as st
import pandas as pd
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

st.set_page_config(page_title="SKU 채용 정보 추천", layout="wide")

st.title("SKU 채용 정보 추천 시스템")

@st.cache_data
def load_data():
    try:
        current_dir = Path(__file__).parent
        csv_path = current_dir / "recruiment_body_crawling" / "skuniv_recruitment_body.csv"
        
        if csv_path.exists():
            df = pd.read_csv(str(csv_path))
            return df
        else:
            st.error(f"파일을 찾을 수 없습니다: {csv_path}")
            return None
    except Exception as e:
        st.error(f"파일 로드 오류: {str(e)}")
        return None

df = load_data()

if df is not None:
    tab1, tab2 = st.tabs(["🔍 키워드 검색", "✨ 맞춤 추천"])
    
    with tab1:
        st.sidebar.header("검색 옵션")
        
        keyword = st.sidebar.text_input("직무 키워드 검색", placeholder="예: 개발, 마케팅, 디자인")
        
        if keyword:
            mask = df["title"].str.contains(keyword, case=False, na=False) | \
                   df["content"].str.contains(keyword, case=False, na=False)
            filtered_df = df[mask]
        else:
            filtered_df = df
        
        st.subheader(f"검색 결과: {len(filtered_df)}개")
        
        if len(filtered_df) > 0:
            for idx, row in filtered_df.iterrows():
                with st.expander(f"📌 [{row["number"]}] {row["title"][:50]}"):
                    st.write("**제목:**", row["title"])
                    st.write("**번호:**", row["number"])
                    st.write("**링크:**", f"[자세히 보기]({row["url"]})")
                    st.write("**내용:**")
                    st.text(row["content"][:500] + "..." if len(str(row["content"])) > 500 else row["content"])
        else:
            st.info("검색 결과가 없습니다.")
    
    with tab2:
        st.header("나에게 맞는 채용 공고 추천받기")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💼 관심 분야")
            interests = st.text_area(
                "관심 있는 직무나 분야를 입력하세요",
                placeholder="예: 웹 개발, 프론트엔드, UI/UX 디자인, 데이터 분석",
                height=100
            )
        
        with col2:
            st.subheader("🛠️ 보유 기술/경험")
            skills = st.text_area(
                "보유한 기술이나 경험을 입력하세요",
                placeholder="예: Python, JavaScript, React, 팀 프로젝트 경험",
                height=100
            )
        
        num_recommendations = st.slider("추천 받을 공고 수", 3, 20, 10)
        
        if st.button("🎯 맞춤 추천 받기", type="primary"):
            if interests or skills:
                user_profile = f"{interests} {skills}"
                
                with st.spinner("추천 공고를 찾는 중..."):
                    df["combined_text"] = df["title"].fillna("") + " " + df["content"].fillna("")
     
                    tfidf = TfidfVectorizer(max_features=1000, stop_words=None)
                    
                    tfidf_matrix = tfidf.fit_transform(df["combined_text"])
                    
                    user_vector = tfidf.transform([user_profile])
                    
                    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
                    
                    df["similarity_score"] = similarities
                    
                    recommendations = df.nlargest(num_recommendations, "similarity_score")
                
                st.success(f"✅ {len(recommendations)}개의 맞춤 공고를 찾았습니다!")
                
                for idx, row in recommendations.iterrows():
                    similarity_percentage = row["similarity_score"] * 100
                    
                    # 유사도에 따른 이모지
                    if similarity_percentage > 30:
                        emoji = "🔥"
                    elif similarity_percentage > 20:
                        emoji = "⭐"
                    elif similarity_percentage > 10:
                        emoji = "👍"
                    else:
                        emoji = "📌"
                    
                    with st.expander(f"{emoji} [{row["number"]}] {row["title"][:50]} - 매칭도: {similarity_percentage:.1f}%"):
                        # 진행률 바로 매칭도 표시
                        st.progress(min(row["similarity_score"], 1.0))
                        
                        st.write("**제목:**", row["title"])
                        st.write("**번호:**", row["number"])
                        st.write("**링크:**", f"[자세히 보기]({row["url"]})")
                        st.write("**내용:**")
                        st.text(row["content"][:500] + "..." if len(str(row["content"])) > 500 else row["content"])
                        
                        if similarity_percentage > 10:
                            st.info(f"💡 이 공고는 입력하신 정보와 {similarity_percentage:.1f}% 일치합니다.")
            else:
                st.warning("⚠️ 관심 분야나 보유 기술을 입력해주세요.")
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 통계")
    st.sidebar.metric("전체 채용 공고", len(df))
    if "filtered_df" in locals():
        st.sidebar.metric("검색된 공고", len(filtered_df))
else:
    st.error("데이터를 로드할 수 없습니다.")
