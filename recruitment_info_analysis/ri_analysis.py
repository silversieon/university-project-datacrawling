import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

def analysis_recruit_info(titles):
    titles = [normalize_title(t) for t in titles]
    labels = [make_label(t) for t in titles]

    X_trainT, X_testT, Y_train, Y_test = train_test_split(titles, labels, test_size=0.3, random_state=0)

    vectorizer = TfidfVectorizer(min_df=3, max_df=0.8)

    X_train = vectorizer.fit_transform(X_trainT)
    X_test = vectorizer.transform(X_testT)

    lr_ri = LogisticRegression()
    lr_ri.fit(X_train, Y_train)

    Y_predict = lr_ri.predict(X_test)

    print("Confusion Matrix(오차 행렬)")
    print(confusion_matrix(Y_test, Y_predict))
    print("\nPrecision Score(정밀도):",
        precision_score(Y_test, Y_predict, average="macro", zero_division=0))
    print("Recall Score(재현율):",
        recall_score(Y_test, Y_predict, average="macro", zero_division=0))
    print("F1 Score(F1 스코어):",
        f1_score(Y_test, Y_predict, average="macro", zero_division=0))

def make_label(title):
    if "IT" in title:
        return 0
    elif "기획" in title:
        return 1
    elif "금융" in title:
        return 2
    elif "건설" in title:
        return 3
    elif "디자인" in title:
        return 4
    else:
        return 5

def normalize_title(title):
    title = title.upper()

    # IT / 시스템 / 개발자
    for keyword in ["S/W", "SW", "개발자", "개발", "엔지니어", "시스템"]:
        if keyword in title:
            title = title.replace(keyword, "IT")

    # 기획 / 마케팅
    for keyword in ["기획", "마케팅", "콘텐츠", "브랜드", "홍보"]:
        if keyword in title:
            title = title.replace(keyword, "기획")

    # 금융 / 증권
    for keyword in ["금융", "증권", "투자", "은행"]:
        if keyword in title:
            title = title.replace(keyword, "금융")

    # 건설 / 시공
    for keyword in ["건설", "시공", "토목"]:
        if keyword in title:
            title = title.replace(keyword, "건설")

    # 디자인 / 편집
    for keyword in ["디자인", "편집", "그래픽", "영상"]:
        if keyword in title:
            title = title.replace(keyword, "디자인")

    return title

def analysis_skuniv_recruit_info():
    data = pd.read_csv("./skuniv_recruitment_titles.csv", encoding="utf-8-sig")

    titles = data['title'].tolist()
    analysis_recruit_info(titles)

def analysis_jobkorea_recruit_info():
    data = pd.read_csv("./jobkorea_recruitment_titles.csv", encoding="utf-8-sig")

    titles = data['title'].tolist()
    analysis_recruit_info(titles)


print("\n========교내 채용 제목 분석============")
analysis_skuniv_recruit_info()

print("\n========잡코리아 채용 제목 분석============")
analysis_jobkorea_recruit_info()