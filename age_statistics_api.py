from fastapi import APIRouter
from API.age_voice_phising.age_vp import request_age_api
router = APIRouter()

def evaluate(pre_grow_rate, mean_grow_rate):
    # (이전 년도 대비 증가율이 평균 대비 증가율 보다 중요한 지표라고 생각하여 0.7이라는 가중치를 주었습니다!)
    hazardScore = pre_grow_rate * 0.7 + mean_grow_rate * 0.3
    return hazardScore, True if hazardScore >= 20 else False

@router.get("")
def get_age_hazard_statistics():
    # 연령별 보이스피싱 피해 건수 불러오기, 컬럼명 정리
    data = request_age_api()
    data = data.rename(columns={'구분':'연도'})
    data = data.set_index('연도')
    age_columns = data.columns

    # 이전 년도 대비 증가율 분석
    latest_year = data.index.max()
    pre_year = latest_year-1
    pre_grow_rate = (data.loc[latest_year] - data.loc[pre_year])/data.loc[pre_year] * 100

    # 평균 대비 증가율 분석
    mean = data.drop(latest_year).mean()
    mean_grow_rate = (data.loc[latest_year] - mean)/mean * 100

    # 해당 연령대의 올해 보이스피싱 위험성 평가 api 응답 생성
    response = {}
    for age in age_columns:
        score, hazard = evaluate(pre_grow_rate[age], mean_grow_rate[age])
        response[age] = {
            "growth_rate_compared_pre_year": round(pre_grow_rate[age], 2),
            "growth_rate_compared_mean_year": round(mean_grow_rate[age], 2),
            "hazardScore": round(score, 2),
            "isHazard": hazard
        }

    return response