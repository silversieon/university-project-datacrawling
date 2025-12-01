import uvicorn
from API.regional_voice_phishing.regional_vp import regional_voice_phishing
from API.age_voice_phising.age_vp import age_voice_phishing
from API.cyber_crime_deep_analysis.cyber_crime_deep_a1 import property_crime
from API.cyber_crime_deep_analysis.cyber_crime_deep_a2 import fraud_damage
from API.cyber_crime_deep_analysis.cyber_crime_deep_a3 import online_activity
from fastapi import FastAPI
from regional_statistics_api import router as rs_router
from age_statistics_api import router as as_router

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

def main():
    regional_voice_phishing()
    age_voice_phishing()
    property_crime()
    fraud_damage()
    online_activity()


if __name__ == "__main__":
    main()
    
    print("API 서버를 시작합니다 (http://127.0.0.1:8000/docs)")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)