from konlpy.tag import Okt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso, LinearRegression
import matplotlib.pyplot as plt
import platform

if platform.system() == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif platform.system() == "Darwin":
    plt.rc("font", family="AppleGothic")
else:
    plt.rc("font", family="NanumGothic")

# linear 회귀분석은 불필요한 값에 계수를 매기므로 활용 제외!!
def linear_regression(X, Y):
    lr = LinearRegression()
    lr.fit(X, Y)

    linear_df = pd.DataFrame({
        "word": tfidf.get_feature_names_out(),
        "linear_coef": lr.coef_
    }).sort_values("linear_coef", ascending=False)

    linear_df.to_csv("./linear_result.csv", index=False, encoding="utf-8-sig")

def lasso_regression(X, Y):
    lasso = Lasso(alpha=0.001)
    lasso.fit(X, Y)

    lasso_df = pd.DataFrame({
        "word": tfidf.get_feature_names_out(),
        "lasso_coef": lasso.coef_
    })

    lasso_words = (
        lasso_df[lasso_df["lasso_coef"] != 0]
        .sort_values("lasso_coef", ascending=False)
    )

    lasso_words.to_csv("./lasso_result.csv", index=False, encoding="utf-8-sig")

    lasso_words = lasso_words.iloc[:10]

    plt.figure(figsize=(8, 6))
    plt.barh(lasso_words['word'][::-1], lasso_words['lasso_coef'][::-1])
    plt.xlabel("Lasso 계수")
    plt.title("조회수에 긍정적 영향을 준 키워드 Top 10")
    plt.tight_layout()
    plt.savefig("lasso_top10.png", dpi=300, bbox_inches="tight")
    plt.close()


def top_views(data):
    top_views = (data[["작성일", "제목", "조회수"]].sort_values("조회수", ascending=False).head(20))

    top_views.to_csv("top_views.csv", index=False, encoding="utf-8-sig")

    top_views = top_views.iloc[:10]

    plt.figure(figsize=(8, 6))
    plt.barh(top_views['제목'][::-1], top_views['조회수'][::-1])
    plt.xlabel("조회수")
    plt.title("공지사항 조회수 TOP 10")
    plt.tight_layout()
    plt.savefig("top_views10.png", dpi=300, bbox_inches="tight")


data = pd.read_csv("./skuniv_notice_2024_2025.csv", encoding="utf-8-sig")

if not data.empty:
    okt = Okt()

    for i in range(len(data)):
        title = str(data.loc[i, "제목"])
        N = okt.nouns(title)
        data.loc[i, "title_N"] = " ".join(N)

    tfidf = TfidfVectorizer(min_df=5, max_df=0.8, max_features=3000)
    
    X = tfidf.fit_transform(data["title_N"])

    scaler = StandardScaler()
    Y = scaler.fit_transform(data[["조회수"]]).ravel()

    # linear_regression(X, Y)
    lasso_regression(X, Y)
    top_views(data)
else:
    print("data가 없습니다.")