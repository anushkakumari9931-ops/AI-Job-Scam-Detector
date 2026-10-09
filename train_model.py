import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


def main() -> None:
    df = pd.read_csv("job_scam_data.csv")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.25,
        random_state=42,
        stratify=df["label"],
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))),
        ("model", LogisticRegression(max_iter=1000, random_state=42)),
    ])

    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, pred)

    print(f"Prototype test accuracy: {accuracy:.2%}")
    print("\nClassification report:")
    print(classification_report(y_test, pred))

    joblib.dump(pipeline, "job_scam_model.joblib")
    print("Saved job_scam_model.joblib")


if __name__ == "__main__":
    main()
