# URL Detector

A Streamlit web app that uses a K-Nearest Neighbors (KNN) classifier to estimate whether a URL is benign or phishing, based on URL-derived features.

## Features

- Accepts a URL and predicts `Benign` or `Phishing`.
- Shows the model's test-set accuracy and a neighbor-based confidence estimate.
- Displays the URL length, digit count, selected special-character count, subdomain count, and whether an IPv4-shaped string is present.
- Trains from the included labeled CSV when the app starts; no separate model download is required.

## How It Works

1. Rows missing a URL or label, and rows with labels other than `benign` or `phishing`, are excluded.
2. Five lexical features are extracted from each URL: length, digit count, selected special-character count, subdomain count, and IPv4 syntax presence.
3. The data is split into training and test sets (80% / 20%) with stratification and a fixed random seed (`42`).
4. `StandardScaler` is fit on the training features, then a 5-neighbor KNN classifier is trained.
5. The displayed accuracy is measured on the held-out test set. For a submitted URL, the app scales the same features and displays the predicted class and KNN class probabilities.

The displayed probability is based on the neighboring training examples. It is not a calibrated risk score or a guarantee that a URL is safe or malicious.

## Dataset

The repository includes `urls.csv` with 235,795 records and these columns:

| Column | Description |
| --- | --- |
| `URL` | URL used for feature extraction |
| `Domain` | Domain value included in the source dataset; not currently used by the model |
| `label` | Class label (`benign` or `phishing`) |
| `length` | Length value included in the source dataset; the app currently calculates URL length itself |

The supplied data contains 134,850 `benign` and 100,945 `phishing` rows. The app reads the CSV locally and uses the `URL` and `label` columns.

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

## Run Locally

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in that terminal and activate again. Alternatively, call `.\.venv\Scripts\python.exe -m streamlit run app.py` without activating the environment.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`.

## Project Structure

```text
.
|-- app.py
|-- urls.csv
|-- requirements.txt
|-- README.md
`-- .gitignore
```

Virtual environments, caches, and local Streamlit secrets should not be committed.

## Limitations and Responsible Use

- The model uses a small set of lexical URL signals and does not inspect page content, DNS, TLS certificates, redirects, or live threat intelligence.
- A legitimate-looking URL can be malicious, and a benign URL can receive a phishing prediction. Do not use this demo as the only security control or open suspicious URLs to verify a prediction.
- Accuracy alone does not describe false-positive and false-negative behavior; precision, recall, class-specific metrics, and validation on recent unseen data should be examined before operational use.
- KNN probabilities are neighbor proportions, not calibrated probabilities.
- The feature extractor is a demonstration and is not a standards-compliant URL parser or a complete domain/subdomain analyzer.

## Future Scope

- Add precision, recall, F1, confusion matrix, ROC-AUC, and class-specific evaluation to the interface and project documentation.
- Deduplicate records and establish leakage-resistant, time-aware evaluation on newer unseen URLs.
- Expand URL parsing and features to cover internationalized domains, ports, paths, redirects, and carefully validated domain signals.
- Compare and tune models using cross-validation, and calibrate probabilities if confidence scores are retained.
- Persist a versioned preprocessing/model pipeline to avoid retraining on every app start.
- Add input validation, larger-dataset performance improvements, automated tests, and clear dataset provenance/versioning.
- Explore optional reputation-service integrations with explicit consent, privacy safeguards, and graceful offline behavior.

## Technology

Python, Streamlit, pandas, NumPy, and scikit-learn.