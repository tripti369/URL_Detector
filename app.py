import re
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score


# Page configuration
st.set_page_config(
    page_title="Phishing URL Detector",
    layout="centered"
)


# Feature extraction
def extract_features(url):
    url = str(url).strip().lower()

    return {
        "url_length": len(url),
        "count_digits": sum(c.isdigit() for c in url),
        "count_special_chars": len(
            re.findall(r"[-_?=@&%]", url)
        ),
        "subdomain_count": max(
            0,
            url.split("/")[2].count(".") - 1
        ) if "://" in url else max(
            0,
            url.split("/")[0].count(".") - 1
        ),
        "has_ip_syntax": 1 if re.search(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            url
        ) else 0
    }


# Load dataset from the project root or a data subdirectory.
script_dir = Path(__file__).resolve().parent
project_dirs = (script_dir, script_dir.parent)
candidate_paths = [
    directory / filename
    for directory in project_dirs
    for filename in ("urls.csv", "urls", "data/urls.csv", "data/urls")
]

dataset_path = next((path for path in candidate_paths if path.exists()), None)
if dataset_path is None:
    raise FileNotFoundError(
        "Could not find the dataset file. Expected one of: "
        + ", ".join(str(path) for path in candidate_paths)
    )

df = pd.read_csv(dataset_path)

# Remove missing values
df = df.dropna(subset=["URL", "label"])

# Convert labels to numbers
df["target"] = df["label"].str.lower().map({
    "benign": 0,
    "phishing": 1
})

# Remove rows with unknown labels
df = df.dropna(subset=["target"])


# Extract features from all URLs
features = pd.DataFrame(
    [extract_features(url) for url in df["URL"]]
)

feature_cols = [
    "url_length",
    "count_digits",
    "count_special_chars",
    "subdomain_count",
    "has_ip_syntax"
]

X = features[feature_cols]
y = df["target"]


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y # use to ensure about majority and minority classes are represented in both train and test sets eg 80 percent female and 20 percent male in both train and test sets.
)


# Scale features
scaler = StandardScaler()# to scale the features to have mean 0 and variance 1, which is important for KNN as it is distance-based and sensitive to feature scales.

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# Train KNN
knn = KNeighborsClassifier(
    n_neighbors=5
)

knn.fit(X_train, y_train)


# Check accuracy
y_pred = knn.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)


# Streamlit interface
st.title("Phishing URL Detector")

st.caption(
    "K-Nearest Neighbors (KNN) based URL classification"
)

st.write(
    f"Model Accuracy: {accuracy * 100:.2f}%"
)


# URL input
test_url = st.text_input(
    "Enter a URL:",
    value="http://login-verify-9912.paypal-sec.com/auth?token=831"
)


if st.button("Analyze URL", type="primary"):

    # Extract features
    extracted = extract_features(test_url)

    input_data = np.array([
        [extracted[col] for col in feature_cols]
    ])

    # Scale input
    input_scaled = scaler.transform(input_data)

    # Prediction
    prediction = knn.predict(input_scaled)[0]

    probabilities = knn.predict_proba(input_scaled)[0]


    # Display result
    st.divider()

    if prediction == 1:

        st.error(
            f"Result: Phishing / Malicious URL "
            f"(Confidence: {probabilities[1] * 100:.1f}%)"
        )

    else:

        st.success(
            f"Result: Legitimate URL "
            f"(Confidence: {probabilities[0] * 100:.1f}%)"
        )


    # Display extracted features
    st.markdown("### Extracted URL Features")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "URL Length",
        extracted["url_length"]
    )

    col2.metric(
        "Digit Count",
        extracted["count_digits"]
    )

    col3.metric(
        "Special Characters",
        extracted["count_special_chars"]
    )

    col4, col5 = st.columns(2)

    col4.metric(
        "Subdomain Count",
        extracted["subdomain_count"]
    )

    col5.metric(
        "Contains IP Address",
        "Yes" if extracted["has_ip_syntax"] else "No"
    )