import uvicorn
import subprocess
import time
import os
from fastapi import FastAPI
from dotenv import load_dotenv

from API.regional_voice_phishing.regional_vp import regional_voice_phishing
from API.age_voice_phising.age_vp import age_voice_phishing
from API.cyber_crime_deep_analysis.cyber_crime_deep_a1 import property_crime
from API.cyber_crime_deep_analysis.cyber_crime_deep_a2 import fraud_damage
from API.cyber_crime_deep_analysis.cyber_crime_deep_a3 import online_activity
from API.internet_banking_usage.ibu_main import internet_banking_usage_analysis
from API.cyber_crime_analysis.cca_main import cyber_crime_trend_analysis

from regional_statistics_api import router as rs_router
from age_statistics_api import router as as_router

load_dotenv()

app = FastAPI(
    title = "Cyber Financial Crime Statistics API",
    description= "Made by Sieon Keum & Yebin Lee (SKU DataCrawling Project)",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs"
)

app.include_router(rs_router, prefix="/api/regionalStatistics", tags=["regional"])
app.include_router(as_router, prefix="/api/ageStatistics", tags=["age"])

@app.get("/")
def root():
    return {"Thank you for your interest in the Cyber Financial Crime Statistics API Server":
    "Made by Yebin Lee & Sieon Keum (SKU DataCrawling Project)"}

def run_etl_pipeline():
    try:
        regional_voice_phishing()
        age_voice_phishing()
        property_crime()
        fraud_damage()
        online_activity()
        internet_banking_usage_analysis()
        cyber_crime_trend_analysis()
        print("모든 데이터 분석 및 이미지 생성이 완료되었습니다.")
    except Exception as e:
        print(f"분석 중 오류 발생: {e}")

if __name__ == "__main__":
    run_etl_pipeline()
    print("Frontend: Streamlit (http://localhost:8501)")
    print("Backend : FastAPI (http://localhost:8000/docs)")

    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "app.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        streamlit_process.terminate()