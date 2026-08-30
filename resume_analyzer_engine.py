"""
Resume Analyzer Engine
======================
Evidence-based resume categorization and job-match scoring.

Design principle: the category assigned to a resume must be justified by
SPECIFIC PHRASES AND SKILLS actually found in the resume text — never by a
black-box probability from a model trained on incomplete/messy labels.
This is what makes it "fact-based" rather than assumption-based: someone
with an Electronics Engineering degree who is working as a Data Analyst
will be scored on the data-analyst language in their resume (SQL, Power BI,
dashboards, etc.), not on the word "engineering" in their degree title.
"""

import re

# ------------------------------------------------------------------
# 1. TAXONOMY
# Each category has:
#   - title_phrases: strong, explicit signals (a person who WRITES these
#     phrases is very likely doing that job right now) -> weight 3
#   - core_skills: tools / techniques associated with the role -> weight 1
# Extend this dictionary any time you want to support a new category.
# ------------------------------------------------------------------

CATEGORY_TAXONOMY = {
    "Data Analyst": {
        "title_phrases": ["data analyst", "data analysis", "reporting analyst",
                           "business intelligence analyst", "bi analyst"],
        "core_skills": ["sql", "excel", "power bi", "tableau", "data visualization",
                         "dashboard", "data cleaning", "data wrangling", "statistics",
                         "a b testing", "python", "pandas", "numpy", "google sheets",
                         "looker", "kpi", "business intelligence", "data mining", "etl",
                         "google analytics", "regression analysis", "pivot table"],
    },
    "Data Scientist": {
        "title_phrases": ["data scientist", "data science"],
        "core_skills": ["machine learning", "deep learning", "python", "r programming",
                         "tensorflow", "pytorch", "scikit learn", "predictive modeling",
                         "nlp", "natural language processing", "computer vision",
                         "feature engineering", "model deployment", "big data", "spark",
                         "hadoop", "statistics", "a b testing", "clustering", "classification"],
    },
    "Machine Learning Engineer": {
        "title_phrases": ["machine learning engineer", "ml engineer", "ai engineer"],
        "core_skills": ["tensorflow", "pytorch", "keras", "mlops", "model deployment",
                         "docker", "kubernetes", "computer vision", "nlp", "deep learning",
                         "neural network", "feature engineering", "model training", "cuda"],
    },
    "Business Analyst": {
        "title_phrases": ["business analyst", "requirements gathering", "business requirements"],
        "core_skills": ["sql", "excel", "stakeholder management", "process improvement",
                         "requirements analysis", "jira", "confluence", "business intelligence",
                         "power bi", "tableau", "gap analysis", "use case", "user story"],
    },
    "Software Engineer": {
        "title_phrases": ["software engineer", "software developer", "full stack developer",
                           "application developer"],
        "core_skills": ["java", "python", "c++", "javascript", "react", "node js", "git",
                         "rest api", "microservices", "docker", "kubernetes", "sql",
                         "object oriented programming", "data structures", "algorithms",
                         "unit testing", "ci cd"],
    },
    "Frontend Developer": {
        "title_phrases": ["frontend developer", "front end developer", "ui developer"],
        "core_skills": ["html", "css", "javascript", "react", "angular", "vue", "typescript",
                         "responsive design", "webpack", "sass", "redux", "tailwind"],
    },
    "Backend Developer": {
        "title_phrases": ["backend developer", "back end developer", "server side developer"],
        "core_skills": ["node js", "java", "python", "django", "flask", "spring boot",
                         "rest api", "sql", "mongodb", "microservices", "docker", "redis"],
    },
    "DevOps Engineer": {
        "title_phrases": ["devops engineer", "site reliability engineer", "sre"],
        "core_skills": ["docker", "kubernetes", "jenkins", "ci cd", "terraform", "ansible",
                         "aws", "azure", "gcp", "linux", "monitoring", "prometheus", "grafana"],
    },
    "Cloud Engineer": {
        "title_phrases": ["cloud engineer", "cloud architect", "cloud administrator"],
        "core_skills": ["aws", "azure", "google cloud", "terraform", "kubernetes", "docker",
                         "cloud migration", "iam", "vpc", "lambda", "cloudformation"],
    },
    "Cybersecurity Analyst": {
        "title_phrases": ["cybersecurity analyst", "security analyst", "information security",
                           "penetration tester", "soc analyst"],
        "core_skills": ["siem", "firewall", "vulnerability assessment", "penetration testing",
                         "network security", "incident response", "encryption", "nist",
                         "iso 27001", "threat intelligence"],
    },
    "Network Engineer": {
        "title_phrases": ["network engineer", "network administrator"],
        "core_skills": ["cisco", "routing", "switching", "tcp ip", "vpn", "firewall",
                         "lan", "wan", "network security", "ccna", "load balancer"],
    },
    "QA / Test Engineer": {
        "title_phrases": ["qa engineer", "test engineer", "quality assurance",
                           "automation testing", "manual testing"],
        "core_skills": ["selenium", "test cases", "regression testing", "bug tracking",
                         "jira", "automation testing", "postman", "test plan", "junit", "cypress"],
    },
    "Electronics Engineer": {
        "title_phrases": ["electronics engineer", "embedded systems engineer",
                           "electronics and communication"],
        "core_skills": ["circuit design", "pcb design", "microcontroller", "embedded systems",
                         "vlsi", "fpga", "arduino", "raspberry pi", "matlab", "simulink",
                         "signal processing", "verilog", "vhdl", "iot", "embedded c"],
    },
    "Electrical Engineer": {
        "title_phrases": ["electrical engineer", "power systems engineer"],
        "core_skills": ["power systems", "circuit analysis", "matlab", "autocad electrical",
                         "plc", "scada", "transformer", "electrical design", "motor control"],
    },
    "Mechanical Engineer": {
        "title_phrases": ["mechanical engineer", "design engineer"],
        "core_skills": ["autocad", "solidworks", "catia", "ansys", "cad", "thermodynamics",
                         "manufacturing", "gd t", "cnc", "product design", "hvac"],
    },
    "Civil Engineer": {
        "title_phrases": ["civil engineer", "structural engineer", "site engineer"],
        "core_skills": ["autocad", "structural analysis", "staad pro", "revit", "surveying",
                         "construction management", "estimation", "concrete design", "bim"],
    },
    "Human Resources": {
        "title_phrases": ["hr generalist", "human resources", "hr manager", "hr administrator",
                           "talent acquisition", "recruiter"],
        "core_skills": ["recruitment", "onboarding", "payroll", "employee relations",
                         "performance management", "hris", "compensation", "benefits administration",
                         "labor relations", "training and development"],
    },
    "Marketing": {
        "title_phrases": ["marketing manager", "marketing specialist", "brand manager"],
        "core_skills": ["seo", "sem", "social media marketing", "content marketing",
                         "brand strategy", "market research", "campaign management",
                         "google ads", "email marketing", "crm"],
    },
    "Digital Marketing": {
        "title_phrases": ["digital marketing", "seo specialist", "performance marketing"],
        "core_skills": ["seo", "sem", "google ads", "facebook ads", "google analytics",
                         "content strategy", "ppc", "social media marketing", "email marketing",
                         "conversion rate optimization"],
    },
    "Sales": {
        "title_phrases": ["sales executive", "sales representative", "account executive",
                           "business development executive"],
        "core_skills": ["lead generation", "crm", "salesforce", "negotiation",
                         "client relationship management", "cold calling", "quota attainment",
                         "pipeline management", "b2b sales", "closing deals"],
    },
    "Accountant": {
        "title_phrases": ["accountant", "accounts payable", "accounts receivable",
                           "bookkeeper"],
        "core_skills": ["quickbooks", "accounts payable", "accounts receivable",
                         "general ledger", "reconciliation", "tally", "gaap", "tax preparation",
                         "financial statements", "sap fico", "auditing"],
    },
    "Finance": {
        "title_phrases": ["financial analyst", "finance manager", "investment analyst"],
        "core_skills": ["financial modeling", "valuation", "budgeting", "forecasting",
                         "excel", "financial statements", "variance analysis", "risk analysis",
                         "capital budgeting", "financial reporting"],
    },
    "Banking": {
        "title_phrases": ["bank teller", "loan officer", "relationship manager", "banking"],
        "core_skills": ["loan processing", "credit analysis", "kyc", "compliance",
                         "risk management", "underwriting", "banking operations", "aml"],
    },
    "Consultant": {
        "title_phrases": ["management consultant", "business consultant", "strategy consultant"],
        "core_skills": ["stakeholder management", "process improvement", "strategy",
                         "change management", "client engagement", "presentation", "powerpoint"],
    },
    "Project Manager": {
        "title_phrases": ["project manager", "program manager", "scrum master"],
        "core_skills": ["agile", "scrum", "jira", "risk management", "stakeholder management",
                         "project planning", "budget management", "pmp", "kanban", "gantt chart"],
    },
    "Product Manager": {
        "title_phrases": ["product manager", "product owner"],
        "core_skills": ["product roadmap", "user research", "agile", "product strategy",
                         "a b testing", "wireframing", "stakeholder management", "kpi",
                         "market research", "backlog management"],
    },
    "Healthcare": {
        "title_phrases": ["registered nurse", "medical assistant", "healthcare provider",
                           "clinical"],
        "core_skills": ["patient care", "electronic health records", "clinical documentation",
                         "hipaa", "medical terminology", "vital signs", "care coordination"],
    },
    "Teacher": {
        "title_phrases": ["teacher", "educator", "instructor", "lecturer"],
        "core_skills": ["curriculum development", "lesson planning", "classroom management",
                         "student assessment", "differentiated instruction", "e learning"],
    },
    "Designer": {
        "title_phrases": ["graphic designer", "ui ux designer", "product designer"],
        "core_skills": ["figma", "adobe photoshop", "adobe illustrator", "sketch",
                         "wireframing", "prototyping", "user research", "typography",
                         "adobe xd", "design systems"],
    },
    "Content Writer": {
        "title_phrases": ["content writer", "copywriter", "technical writer"],
        "core_skills": ["content strategy", "seo writing", "editing", "proofreading",
                         "storytelling", "cms", "wordpress", "content calendar"],
    },
    "Public Relations": {
        "title_phrases": ["public relations", "pr specialist", "communications specialist"],
        "core_skills": ["press release", "media relations", "crisis communication",
                         "brand reputation", "stakeholder communication", "social media"],
    },
    "Legal / Advocate": {
        "title_phrases": ["advocate", "lawyer", "legal counsel", "paralegal"],
        "core_skills": ["litigation", "legal research", "contract drafting", "compliance",
                         "case management", "legal documentation", "negotiation"],
    },
    "Chef / Culinary": {
        "title_phrases": ["chef", "sous chef", "culinary", "line cook"],
        "core_skills": ["menu planning", "food safety", "kitchen management", "inventory control",
                         "plating", "haccp", "food cost control"],
    },
    "Aviation": {
        "title_phrases": ["pilot", "flight attendant", "aviation", "aircraft maintenance"],
        "core_skills": ["faa regulations", "flight operations", "aircraft systems",
                         "safety compliance", "ground operations"],
    },
    "Construction": {
        "title_phrases": ["construction manager", "site supervisor", "construction"],
        "core_skills": ["blueprint reading", "project scheduling", "osha", "cost estimation",
                         "quality control", "subcontractor management"],
    },
    "Customer Support / BPO": {
        "title_phrases": ["customer support", "customer service representative", "bpo",
                           "call center"],
        "core_skills": ["customer service", "crm", "ticketing system", "conflict resolution",
                         "zendesk", "live chat support"],
    },
}

# Union of every skill/phrase across all categories, used for the resume<->JD
# skill-gap comparison (independent of which category is finally chosen).
ALL_SKILLS = sorted({
    skill
    for cat in CATEGORY_TAXONOMY.values()
    for skill in (cat["core_skills"] + cat["title_phrases"])
})


# ------------------------------------------------------------------
# 2. TEXT UTILITIES
# ------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Lowercase, strip punctuation (so multi-word phrases like 'power bi'
    still match), collapse whitespace."""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_phrases(text: str, phrases) -> list:
    """Return the subset of `phrases` that literally appear in `text`.
    Uses word-boundary matching so 'r' doesn't match inside 'director'."""
    found = []
    for phrase in phrases:
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        if re.search(pattern, text):
            found.append(phrase)
    return found


def extract_years_of_experience(text: str):
    """Best-effort extraction of stated years of experience, e.g.
    '5 years of experience' or '3+ years'. Returns None if not found."""
    matches = re.findall(r"(\d{1,2})\s*\+?\s*years?", text)
    years = [int(m) for m in matches if int(m) <= 50]
    return max(years) if years else None


# ------------------------------------------------------------------
# 3. EVIDENCE-BASED CATEGORY SCORING
# ------------------------------------------------------------------

TITLE_WEIGHT = 3
SKILL_WEIGHT = 1
MIN_EVIDENCE_SCORE = 3  # below this, we refuse to guess confidently


def score_categories(resume_text: str, taxonomy: dict = CATEGORY_TAXONOMY) -> list:
    """
    Score every category against the resume using ONLY things literally
    present in the text. Returns a list of dicts sorted by evidence score,
    each with the exact phrases/skills that were matched (for transparency).
    """
    text = clean_text(resume_text)
    results = []

    for category, spec in taxonomy.items():
        title_hits = find_phrases(text, spec["title_phrases"])
        skill_hits = find_phrases(text, spec["core_skills"])

        raw_score = len(title_hits) * TITLE_WEIGHT + len(skill_hits) * SKILL_WEIGHT
        max_possible = len(spec["title_phrases"]) * TITLE_WEIGHT + len(spec["core_skills"]) * SKILL_WEIGHT
        coverage_pct = round((raw_score / max_possible) * 100, 1) if max_possible else 0.0

        results.append({
            "category": category,
            "raw_score": raw_score,
            "coverage_pct": coverage_pct,
            "matched_title_phrases": title_hits,
            "matched_skills": skill_hits,
        })

    results.sort(key=lambda r: r["raw_score"], reverse=True)

    # Convert raw scores into a comparative confidence % across categories
    total = sum(r["raw_score"] for r in results) or 1
    for r in results:
        r["confidence_pct"] = round((r["raw_score"] / total) * 100, 1)

    return results


def classify_resume(resume_text: str, top_n: int = 3, taxonomy: dict = CATEGORY_TAXONOMY) -> dict:
    """
    Returns the top category with its supporting evidence, or an honest
    "not enough evidence" result instead of a forced guess.
    """
    scored = score_categories(resume_text, taxonomy)
    top = scored[:top_n]
    best = scored[0]

    if best["raw_score"] < MIN_EVIDENCE_SCORE:
        return {
            "status": "low_confidence",
            "message": (
                "This resume doesn't contain enough specific role-related "
                "skills or title phrases to confidently assign a category. "
                "Consider adding more concrete tools, technologies, or "
                "responsibilities to the resume text."
            ),
            "top_candidates": top,
        }

    return {
        "status": "ok",
        "predicted_category": best["category"],
        "confidence_pct": best["confidence_pct"],
        "evidence": {
            "matched_title_phrases": best["matched_title_phrases"],
            "matched_skills": best["matched_skills"],
        },
        "top_candidates": top,
    }


# ------------------------------------------------------------------
# 4. RESUME <-> JOB DESCRIPTION MATCHING
# ------------------------------------------------------------------

def _text_similarity(text_a: str, text_b: str) -> float:
    """Cosine similarity over term-frequency vectors (no IDF, since IDF is
    meaningless with only two documents). This is a general content-overlap
    signal, separate from the explicit skill list below."""
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = CountVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        vectors = vectorizer.fit_transform([text_a, text_b])
    except ValueError:
        return 0.0  # empty vocabulary (e.g. one text is blank)
    sim = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return float(sim)


def match_resume_to_job(resume_text: str, job_description: str, skill_list=None) -> dict:
    """
    Returns a full, explainable match report:
      - overall match score (0-100)
      - skills present in both (matched)
      - skills required by the JD but missing from the resume (gap)
      - skills the resume has that the JD didn't ask for (bonus)
      - years-of-experience comparison, if stated in both
    """
    skill_list = skill_list or ALL_SKILLS

    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(job_description)

    resume_skills = set(find_phrases(resume_clean, skill_list))
    jd_skills = set(find_phrases(jd_clean, skill_list))

    matched_skills = sorted(resume_skills & jd_skills)
    missing_skills = sorted(jd_skills - resume_skills)
    bonus_skills = sorted(resume_skills - jd_skills)

    skill_overlap_ratio = (len(matched_skills) / len(jd_skills)) if jd_skills else 0.0
    text_sim = _text_similarity(resume_clean, jd_clean)

    # Weighted blend: explicit skill overlap counts more than raw text
    # overlap, because it's the more literal, defensible signal.
    overall_score = round((0.65 * skill_overlap_ratio + 0.35 * text_sim) * 100, 1)

    resume_years = extract_years_of_experience(resume_clean)
    jd_years = extract_years_of_experience(jd_clean)

    if overall_score >= 75:
        verdict = "Strong match"
    elif overall_score >= 50:
        verdict = "Good match — some gaps to address"
    elif overall_score >= 25:
        verdict = "Partial match — significant gaps"
    else:
        verdict = "Weak match"

    return {
        "overall_match_pct": overall_score,
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "bonus_skills": bonus_skills,
        "skill_overlap_pct": round(skill_overlap_ratio * 100, 1),
        "text_similarity_pct": round(text_sim * 100, 1),
        "resume_years_experience": resume_years,
        "jd_years_experience_required": jd_years,
    }


# ------------------------------------------------------------------
# 5. PDF TEXT EXTRACTION (used by both Colab and Streamlit)
# ------------------------------------------------------------------

def extract_text_from_pdf(file_like_or_path) -> str:
    """Accepts either a filesystem path (str) or a file-like object with
    .read() returning bytes (as Streamlit's uploader provides)."""
    import fitz  # PyMuPDF

    if isinstance(file_like_or_path, str):
        doc = fitz.open(file_like_or_path)
    else:
        pdf_bytes = file_like_or_path.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    doc.close()
    return text


# ------------------------------------------------------------------
# 6. FULL PIPELINE (one call does everything)
# ------------------------------------------------------------------

def analyze(resume_text: str, job_description: str = None) -> dict:
    report = {"category_analysis": classify_resume(resume_text)}
    if job_description:
        report["job_match_analysis"] = match_resume_to_job(resume_text, job_description)
    return report
