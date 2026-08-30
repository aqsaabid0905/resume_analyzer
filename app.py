import streamlit as st
from resume_analyzer_engine import (
    extract_text_from_pdf,
    classify_resume,
    match_resume_to_job,
)

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="wide")

st.title("🤖 AI Resume Analyzer")
st.caption(
    "Evidence-based category detection and job matching — every result is backed "
    "by the exact phrases and skills found in your resume, not a guess."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Upload your resume")
    resume_file = st.file_uploader("PDF format", type=["pdf"])

with col2:
    st.subheader("📋 Paste the job description (optional)")
    job_description = st.text_area("Job description", height=220)

analyze_clicked = st.button("Analyze", type="primary")

if analyze_clicked:
    if not resume_file:
        st.warning("Please upload a resume PDF first.")
        st.stop()

    with st.spinner("Reading resume..."):
        resume_text = extract_text_from_pdf(resume_file)

    if len(resume_text.strip()) < 50:
        st.error("Could not extract meaningful text from this PDF. Is it a scanned image?")
        st.stop()

    st.divider()

    st.header("🎯 Predicted Category")
    result = classify_resume(resume_text)

    if result["status"] == "low_confidence":
        st.warning(result["message"])
        st.write("Closest candidates found (none strong enough to commit to):")
        for c in result["top_candidates"]:
            st.write(f"- **{c['category']}** — {c['raw_score']} evidence points")
    else:
        st.success(f"**{result['predicted_category']}**  ({result['confidence_pct']}% confidence)")

        ev = result["evidence"]
        with st.expander("Why this category? (evidence used)"):
            if ev["matched_title_phrases"]:
                st.write("**Title phrases found in resume:**", ", ".join(ev["matched_title_phrases"]))
            st.write("**Relevant skills found:**", ", ".join(ev["matched_skills"]) or "None")

        st.write("**Other candidate categories considered:**")
        for c in result["top_candidates"][1:]:
            matched = ", ".join(c["matched_skills"]) or "none"
            st.write(f"- {c['category']} — {c['confidence_pct']}% (matched: {matched})")

    if job_description.strip():
        st.divider()
        st.header("📊 Resume <-> Job Description Match")

        match = match_resume_to_job(resume_text, job_description)

        m1, m2, m3 = st.columns(3)
        m1.metric("Overall Match", f"{match['overall_match_pct']}%")
        m2.metric("Skill Overlap", f"{match['skill_overlap_pct']}%")
        m3.metric("Content Similarity", f"{match['text_similarity_pct']}%")

        st.write(f"**Verdict:** {match['verdict']}")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("✅ **Matched Skills**")
            for s in match["matched_skills"]:
                st.write(f"- {s.title()}")
            if not match["matched_skills"]:
                st.write("_None_")

        with c2:
            st.markdown("❌ **Missing Skills (gap)**")
            for s in match["missing_skills"]:
                st.write(f"- {s.title()}")
            if not match["missing_skills"]:
                st.write("_None - great coverage!_")

        with c3:
            st.markdown("➕ **Bonus Skills (not requested by JD)**")
            for s in match["bonus_skills"]:
                st.write(f"- {s.title()}")
            if not match["bonus_skills"]:
                st.write("_None_")
    else:
        st.info("Paste a job description above to also see match score and skill gaps.")
