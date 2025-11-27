from API.regional_voice_phishing.regional_vp import regional_voice_phishing
from API.age_voice_phising.age_vp import age_voice_phishing
from API.cyber_crime_deep_analysis.cyber_crime_deep_a1 import property_crime
from API.cyber_crime_deep_analysis.cyber_crime_deep_a2 import fraud_damage
from API.cyber_crime_deep_analysis.cyber_crime_deep_a3 import online_activity
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

def main():
    # regional_voice_phishing()
    # age_voice_phishing()
    # property_crime()
    # fraud_damage()
    online_activity()


if __name__ == "__main__":
    main()
