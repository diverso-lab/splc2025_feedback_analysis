# 🧠 Feedback Analysis for SPL Forks (SPLC 2025)

This repository contains the scripts and tooling used for analyzing technical feedback in fork-based software product line (SPL) developments. It accompanies the research article *"Feedback Analysis in Software Product Line Forked Developments"*, submitted to SPLC 2025.

The analysis covers:
- Extraction of commits, issues, and pull requests from GitHub forks.
- Automatic tagging of development activity (e.g., `testing`, `fix`, `config`, etc.).
- Linking of activity to features inferred from project structure.
- Aggregation of traceability tuples into a unified **feedback log**.
- High-level visual and textual analysis.

## 🔐 How to Get a GitHub Personal Access Token

1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"** → choose **"Classic token"**
3. Fill in:
   - **Note**: name your token (e.g., `VSCode`)
   - **Expiration**: set duration
   - **Scopes**: check `repo` scope.
4. Click **"Generate token"**
5. **Copy the token immediately!** You won’t be able to see it again.

## 📦 Installation

Clone the repository and set up a virtual environment with Python 3.12:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then export your GitHub token as an environment variable:

```bash
cp .env.example .env
source .env
```

## 🧪 Running the evaluation
The pipeline is divided into four steps:

### Data Collection (Evaluation 01)
Collects commits, issues, and pull requests for all forks listed in forks.json. Results are saved in evaluation/<fork_id>/.

```bash
python evaluation_01_data_source.py
```

### Traceability Map Construction (Evaluation 02)
Processes each fork's data to build traceability tuples of the form:

```
(feature, source_type, tag, timestamp)
```
Saved as traceability_map.json inside each fork's folder.

```bash
python evaluation_02_data_processing.py
```

### Feedback Log Generation (Evaluation 03)
Aggregates all traceability maps into a unified feedback_log.json, including the fork name and timestamp:

```
(feature, source_type, tag, fork, timestamp)
```

Run this script:

```bash
python evaluation_03_feedback_log.py
```

### Global Analysis and Visualization (Evaluation 04)
Performs quantitative and visual analysis from feedback_log.json, including bar charts grouped by semantic categories (e.g., "features with most failures", "features under test", etc.).

```bash
python evaluation_04_analysis.py
python evaluation_05_visuals.py
```

## Output
`feedback_log.json`: Consolidated analysis data.

`figures/*.svg and *.png`: Visual summaries for inclusion in the paper.

Textual summaries printed to console.

## 📚 Citation
If you find this useful, please cite our upcoming paper (to be updated after acceptance).