# 🧠 Feedback Analysis for SPL Forks (SPLC 2025)

This repository contains the scripts and tooling used for analyzing technical feedback in fork-based software product line (SPL) developments. It accompanies the paper *"Feedback Analysis in Software Product Line Forked Developments"*, accepted at SPLC 2025.

The analysis covers:
- Extraction of commits, issues, and pull requests from GitHub forks.
- Automatic tagging of development activity (e.g., `testing`, `fix`, `config`, etc.).
- Linking of activity to features inferred from project structure.
- Aggregation of traceability tuples into a unified **feedback log**.
- High-level visual and textual analysis.

---

## 🐳 Docker Usage (Recommended)

We provide a ready-to-use Docker image:

```bash
docker pull drorganvidez/splc-feedback-artifact:latest
```

Make sure to provide your GitHub Personal Access Token in a `.env` file:

```bash
echo "GITHUB_TOKEN=your_token_here" > .env
```

Then run the container:

```bash
docker run --rm -it \
  --env-file .env \
  -v "$PWD":/app \
  drorganvidez/splc-feedback-artifact:latest
```

Once inside the container, you can run any step of the pipeline as usual:

```bash
python evaluation_03_feedback_log.py
python evaluation_04_analysis.py
```

---

## 🔧 Manual Setup (Python 3.12)

```bash
git clone https://github.com/diverso-lab/splc2025_feedback_analysis
cd splc2025_feedback_analysis

python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
source .env
```

---

## 🧪 Pipeline Overview

The full pipeline consists of 4 steps. You can run steps 3–4 directly using the included data, or perform the full analysis from scratch.

### 🟢 Step 1: Data Collection
Collect commits, issues, and PRs from all forks in `forks.json`:

```bash
python evaluation_01_data_source.py
```

### 🟡 Step 2: Traceability Mapping
Generate tuples of the form:

```
(feature, source_type, tag, fork, timestamp)
```

```bash
python evaluation_02_data_processing.py
```

### 🔵 Step 3: Feedback Log Generation
Aggregate all data into `feedback_log.json`:

```bash
python evaluation_03_feedback_log.py
```

### 🟣 Step 4: Analysis and Visualization
Create summaries and figures:

```bash
python evaluation_04_analysis.py
python evaluation_05_visuals.py
```

---

## 🧪 Proof of Concept

A minimal demo is available for testing purposes:

```bash
python proof_of_concept_01_data_source.py
python proof_of_concept_02_data_processing.py
python proof_of_concept_03_analysis.py
python proof_of_concept_04_charts.py
```

This version uses synthetic data and does not require a GitHub token.

---

## 🔐 GitHub Token Setup

1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"** → choose **"Classic token"**
3. Select scope: `repo`
4. Save the token and add it to a file:

```bash
echo "GITHUB_TOKEN=your_token_here" > .env
```

---

## 📦 Outputs

- `feedback_log.json`: Aggregated feedback tuples.
- `figures/*.svg` and `*.png`: Visual output for publication.
- Console summaries.

---

## 📚 Citation

To cite this artifact, please reference:

> D. Romero-Organvidez, O. Díaz, Y. Tang, D. Benavides. *Feedback Analysis in Software Product Line Forked Developments*. Artifact paper. SPLC 2025. A Coruña, Spain.
