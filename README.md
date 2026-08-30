# AI Resume Analyzer

An evidence-based resume analyzer that:
- Detects the most relevant job category for a resume based on **actual skills and content**, not just degree titles or keywords in isolation.
- Compares a resume against a job description and reports an overall match score.
- Shows matched skills, missing skills (skill gap), and bonus skills.

## How it works

Instead of relying on a black-box machine learning model trained on messy, incomplete labels, this project uses a transparent **evidence-based scoring system**:

- A curated taxonomy of 30+ job categories (Data Analyst, Software Engineer, Electronics Engineer, HR, Marketing, etc.), each with associated title phrases and core skills.
- The resume text is scanned for these phrases/skills, and the category with the strongest evidence wins — with the exact matched phrases shown for transparency.
- If a resume doesn't contain enough specific evidence, the tool honestly says so instead of guessing.

## Files

- `app.py` — Streamlit web app (the user interface)
- `resume_analyzer_engine.py` — Core logic: category detection, skill extraction, job matching
- `requirements.txt` — Python dependencies for deployment
- `AI_Resume_Analyzer.ipynb` — Google Colab notebook version (for quick testing without deployment)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run in Google Colab

Open `AI_Resume_Analyzer.py` in Google Colab and run the cells in order.

## Live Demo
https://resumeanalyzer-hsrq4appyjf9ly96isf3tfs.streamlit.app/ 
