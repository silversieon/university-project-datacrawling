from fastapi import APIRouter
from API.age_voice_phising.age_vp import request_age_api
from sklearn.cluster import KMeans
import numpy as np
router = APIRouter()

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

    X = np.column_stack([
        pre_grow_rate,
        mean_grow_rate
    ])

    # 3개의 군집으로 분류하여 군집분석 (저위험, 중간위험, 고위험)
    kmeans = KMeans(n_clusters=3, random_state=0, n_init='auto')

    # 각 연령대를 3개의 군집으로 나누기
    labels = kmeans.fit_predict(X)

    # (이전 년도 대비 증가율, 평균 대비 증가율) 세 군집의 중앙을 평가
    centers = kmeans.cluster_centers_
    cluster_score = np.argsort(centers.mean(axis=1))

    # 중앙 위치가 작은(두 증가율 평균이 가장 낮은) 군집부터 위험도 배정
    hazard_score = {
        cluster_score[0]: "LOW",
        cluster_score[1]: "MID",
        cluster_score[2]: "HIGH"
    }

    # 해당 연령대의 올해 보이스피싱 위험성 평가 api 응답 생성
    response = {}
    for i, age in enumerate(age_columns):
        response[age] = {
            "growth_rate_compared_pre_year": round(pre_grow_rate[age], 2),
            "growth_rate_compared_mean_year": round(mean_grow_rate[age], 2),
            "cluster": int(labels[i]),
            "isHazard": hazard_score[labels[i]]
        }

    return response