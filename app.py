HEAD
import os
import re
import json
import math
from typing import List, Dict, Tuple, Optional

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------------
# App setup
# -------------------------------
st.set_page_config(
    page_title="Resume Matcher Pro",
    page_icon="📄",
    layout="wide",
)

# -------------------------------
# Styling
# -------------------------------
st.markdown(
    """
    <style>
        .main {
            background: linear-gradient(180deg, #0b1020 0%, #111827 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        h1, h2, h3 {
            color: #f8fafc !important;
        }
        p, label, .stMarkdown, .stCaption {
            color: #dbe4ee !important;
        }
        .app-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.18);
            margin-bottom: 1rem;
        }
        .score-card {
            background: linear-gradient(135deg, rgba(59,130,246,0.22), rgba(16,185,129,0.18));
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 18px;
            padding: 18px;
            text-align: center;
            min-height: 130px;
        }
        .score-title {
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-bottom: 0.35rem;
        }
        .score-value {
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.25rem;
        }
        .score-note {
            font-size: 0.85rem;
            color: #cbd5e1;
        }
        .small-note {
            color: #94a3b8;
            font-size: 0.9rem;
        }
        div[data-testid="stMetricValue"] {
            color: white;
        }
        div[data-testid="stFileUploader"] section {
            background: rgba(255,255,255,0.04);
            border-radius: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 Resume & Job Description Matcher")
st.caption("Upload or paste a resume, compare it to a job description, and get AI-powered improvement suggestions.")


# -------------------------------
# Session state
# -------------------------------
if "resume_input" not in st.session_state:
    st.session_state.resume_input = ""

if "job_input" not in st.session_state:
    st.session_state.job_input = ""

if "report_text" not in st.session_state:
    st.session_state.report_text = ""

if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None


# -------------------------------
# Helpers
# -------------------------------
def create_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


COMMON_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "have", "has", "are", "you",
    "your", "will", "our", "their", "into", "using", "used", "use", "can", "able",
    "such", "across", "about", "role", "team", "work", "working", "build", "building",
    "candidate", "candidates", "experience", "years", "year", "skills", "skill",
    "knowledge", "strong", "excellent", "good", "understanding", "preferred", "plus",
    "including", "ability", "required", "requirements", "responsibilities", "job",
    "description", "resume", "cv", "support", "develop", "development", "engineer",
    "engineering", "data", "ai", "ml"
}

KNOWN_TECH_TERMS = [
    "python", "sql", "tensorflow", "pytorch", "scikit-learn", "sklearn", "pandas",
    "numpy", "matplotlib", "docker", "kubernetes", "aws", "gcp", "azure",
    "fastapi", "flask", "django", "streamlit", "langchain", "llamaindex", "rag",
    "vector database", "pinecone", "faiss", "chroma", "weaviate", "openai",
    "prompt engineering", "llm", "llms", "transformers", "hugging face", "nlp",
    "computer vision", "genai", "generative ai", "git", "github", "jupyter",
    "feature engineering", "model evaluation", "model training", "deep learning",
    "machine learning", "rest api", "api", "etl", "airflow", "spark", "linux",
    "embeddings", "semantic search"
]


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\-\+#\. ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def read_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def extract_keywords(text: str) -> List[str]:
    normalized = clean_text(text)
    found_keywords = set()

    for term in KNOWN_TECH_TERMS:
        if term in normalized:
            found_keywords.add(term)

    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\-\+#\.]{1,}", normalized)
    for token in tokens:
        if token not in COMMON_WORDS and len(token) > 2:
            found_keywords.add(token)

    return sorted(found_keywords)


def calculate_keyword_score(resume_text: str, job_text: str) -> Tuple[int, List[str], List[str]]:
    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_text))

    if not job_keywords:
        return 0, [], []

    matched = sorted(job_keywords.intersection(resume_keywords))
    missing = sorted(job_keywords.difference(resume_keywords))
    score = int((len(matched) / len(job_keywords)) * 100)

    return score, matched, missing


def calculate_tfidf_semantic_score(resume_text: str, job_text: str) -> Tuple[int, str]:
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([resume_text, job_text])
    similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    score = int(round(max(0.0, min(1.0, similarity)) * 100))
    return score, "TF-IDF cosine similarity"


def cosine_from_lists(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def trim_for_embedding(text: str, max_chars: int = 12000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def calculate_semantic_score(
    resume_text: str,
    job_text: str,
    client: Optional[OpenAI],
) -> Tuple[int, str]:
    if client is None:
        return calculate_tfidf_semantic_score(resume_text, job_text)

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[trim_for_embedding(resume_text), trim_for_embedding(job_text)],
        )
        vec_resume = response.data[0].embedding
        vec_job = response.data[1].embedding
        similarity = cosine_from_lists(vec_resume, vec_job)
        score = int(round(max(0.0, min(1.0, similarity)) * 100))
        return score, "OpenAI embeddings"
    except Exception:
        return calculate_tfidf_semantic_score(resume_text, job_text)


def calculate_combined_score(keyword_score: int, semantic_score: int) -> int:
    return int(round((0.45 * keyword_score) + (0.55 * semantic_score)))


def detect_resume_sections(resume_text: str) -> Dict[str, str]:
    section_patterns = {
        "summary": r"(summary|profile|professional summary)",
        "skills": r"(skills|technical skills|core skills)",
        "experience": r"(experience|work experience|employment)",
        "projects": r"(projects|selected projects)",
        "education": r"(education|academic background)",
    }

    lines = resume_text.splitlines()
    sections = {}
    current_section = "general"
    buffer = []

    def save_section(section_name: str, content: List[str]) -> None:
        text = "\n".join(content).strip()
        if text:
            sections[section_name] = text

    for line in lines:
        stripped = line.strip()

        if not stripped:
            buffer.append(line)
            continue

        new_section = None
        for name, pattern in section_patterns.items():
            if re.fullmatch(pattern, stripped.lower()):
                new_section = name
                break

        if new_section:
            save_section(current_section, buffer)
            current_section = new_section
            buffer = []
        else:
            buffer.append(line)

    save_section(current_section, buffer)
    return sections


def display_keywords(items: List[str], limit: int = 30) -> str:
    if not items:
        return "None found"
    return ", ".join(items[:limit])


def get_ai_resume_feedback(
    client: OpenAI,
    resume_text: str,
    job_text: str,
    matched_keywords: List[str],
    missing_keywords: List[str],
    keyword_score: int,
    semantic_score: int,
    combined_score: int,
) -> Dict:
    system_prompt = """
You are an expert recruiter and resume coach.

Compare a candidate's resume with a job description and return:
1. a short fit summary
2. top strengths
3. top gaps
4. an improved professional summary
5. 4 ATS-friendly rewritten resume bullets
6. 5 recommended keywords to add only if truthful
7. a final verdict

Rules:
- Be clear, practical, and professional.
- Do not invent fake experience, fake numbers, or fake technologies.
- Only suggest keywords that genuinely fit the profile.
- Return valid JSON only.
"""

    user_prompt = f"""
RESUME:
{resume_text}

JOB DESCRIPTION:
{job_text}

MATCHED KEYWORDS:
{matched_keywords}

MISSING KEYWORDS:
{missing_keywords}

CURRENT SCORES:
- Keyword Score: {keyword_score}
- Semantic Score: {semantic_score}
- Combined Score: {combined_score}

Return JSON in this format:
{{
  "fit_summary": "string",
  "top_strengths": ["string", "string", "string"],
  "top_gaps": ["string", "string", "string"],
  "improved_summary": "string",
  "rewritten_bullets": ["string", "string", "string", "string"],
  "recommended_keywords": ["string", "string", "string", "string", "string"],
  "final_verdict": "string"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content or ""

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        possible_json = re.search(r"\{.*\}", content, re.DOTALL)
        if possible_json:
            return json.loads(possible_json.group(0))
        raise ValueError("The AI response could not be read as JSON.")


def build_download_report(
    keyword_score: int,
    semantic_score: int,
    semantic_method: str,
    combined_score: int,
    matched_keywords: List[str],
    missing_keywords: List[str],
    feedback: Optional[Dict],
) -> str:
    report = [
        "# Resume Match Report",
        "",
        f"- Keyword Match Score: **{keyword_score}%**",
        f"- Semantic Match Score: **{semantic_score}%**",
        f"- Semantic Method: **{semantic_method}**",
        f"- Combined Match Score: **{combined_score}%**",
        "",
        "## Matched Keywords",
        display_keywords(matched_keywords, limit=100),
        "",
        "## Missing Keywords",
        display_keywords(missing_keywords, limit=100),
        "",
    ]

    if feedback:
        report.extend([
            "## Overall Fit",
            feedback.get("fit_summary", ""),
            "",
            "## Top Strengths",
            *[f"- {item}" for item in feedback.get("top_strengths", [])],
            "",
            "## Top Gaps",
            *[f"- {item}" for item in feedback.get("top_gaps", [])],
            "",
            "## Improved Professional Summary",
            feedback.get("improved_summary", ""),
            "",
            "## Suggested Resume Bullets",
            *[f"- {item}" for item in feedback.get("rewritten_bullets", [])],
            "",
            "## Recommended Keywords",
            ", ".join(feedback.get("recommended_keywords", [])),
            "",
            "## Final Verdict",
            feedback.get("final_verdict", ""),
        ])

    return "\n".join(report)


def score_card(title: str, score: int, note: str) -> None:
    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-title">{title}</div>
            <div class="score-value">{score}%</div>
            <div class="score-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("Tools")
    st.write("Load sample content or upload a PDF resume.")

    if st.button("Load example resume", use_container_width=True):
        st.session_state.resume_input = EXAMPLE_RESUME

    if st.button("Load example job description", use_container_width=True):
        st.session_state.job_input = EXAMPLE_JOB

    if st.button("Load both examples", use_container_width=True):
        st.session_state.resume_input = EXAMPLE_RESUME
        st.session_state.job_input = EXAMPLE_JOB

    st.markdown("---")
    uploaded_resume = st.file_uploader("Upload resume PDF", type=["pdf"])

    if uploaded_resume is not None:
        try:
            extracted_text = read_pdf_text(uploaded_resume)
            st.success(f"PDF read successfully: {uploaded_resume.name}")
            st.caption(f"Extracted {len(extracted_text)} characters")
            if st.button("Use uploaded PDF as resume", use_container_width=True):
                st.session_state.resume_input = extracted_text
        except Exception as error:
            st.error(f"Could not read PDF: {error}")

    st.markdown("---")
    st.info("This app reads OPENAI_API_KEY from your environment. If the key is set, you'll get AI feedback and embedding-based semantic matching.")


# -------------------------------
# Main input area
# -------------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("Resume")
    st.text_area(
        "Paste resume text",
        height=420,
        key="resume_input",
        placeholder="Paste the full resume here or upload a PDF from the sidebar...",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("Job Description")
    st.text_area(
        "Paste job description text",
        height=420,
        key="job_input",
        placeholder="Paste the full job description here...",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

analyze_button = st.button("Analyze Resume Match", use_container_width=True)


# -------------------------------
# Run analysis
# -------------------------------
if analyze_button:
    resume_text = st.session_state.resume_input
    job_text = st.session_state.job_input

    if not resume_text.strip() or not job_text.strip():
        st.error("Please provide both a resume and a job description.")
        st.stop()

    client = create_openai_client()

    keyword_score, matched_keywords, missing_keywords = calculate_keyword_score(resume_text, job_text)
    semantic_score, semantic_method = calculate_semantic_score(resume_text, job_text, client)
    combined_score = calculate_combined_score(keyword_score, semantic_score)
    sections = detect_resume_sections(resume_text)

    st.subheader("Match Overview")

    c1, c2, c3 = st.columns(3)
    with c1:
        score_card("Keyword Match", keyword_score, "Direct overlap between resume and JD keywords")
    with c2:
        score_card("Semantic Match", semantic_score, semantic_method)
    with c3:
        score_card("Combined Score", combined_score, "Weighted mix of keyword and semantic signals")

    st.progress(min(combined_score, 100))

    kw_col, miss_col = st.columns(2)
    with kw_col:
        st.markdown("### Matched Keywords")
        st.write(display_keywords(matched_keywords, limit=50))

    with miss_col:
        st.markdown("### Missing Keywords")
        st.write(display_keywords(missing_keywords, limit=50))

    st.markdown("### Resume Sections Found")
    section_preview = {
        name: (text[:220] + "..." if len(text) > 220 else text)
        for name, text in sections.items()
    }
    st.json(section_preview)

    st.markdown("---")
    st.subheader("AI Suggestions")

    feedback = None
    if client is None:
        st.warning("OPENAI_API_KEY is not set, so AI feedback is disabled. Semantic score is using the local TF-IDF fallback.")
    else:
        try:
            with st.spinner("Reviewing resume and generating suggestions..."):
                feedback = get_ai_resume_feedback(
                    client=client,
                    resume_text=resume_text,
                    job_text=job_text,
                    matched_keywords=matched_keywords,
                    missing_keywords=missing_keywords,
                    keyword_score=keyword_score,
                    semantic_score=semantic_score,
                    combined_score=combined_score,
                )

            st.markdown("### Overall Fit")
            st.write(feedback["fit_summary"])

            strength_col, gap_col = st.columns(2)
            with strength_col:
                st.markdown("### Strong Points")
                for item in feedback["top_strengths"]:
                    st.write(f"- {item}")

            with gap_col:
                st.markdown("### Areas to Improve")
                for item in feedback["top_gaps"]:
                    st.write(f"- {item}")

            st.markdown("### Better Professional Summary")
            st.info(feedback["improved_summary"])

            st.markdown("### Suggested Resume Bullets")
            for bullet in feedback["rewritten_bullets"]:
                st.write(f"- {bullet}")

            st.markdown("### Keywords You Could Add")
            st.write(", ".join(feedback["recommended_keywords"]))

            st.markdown("### Final Recruiter Verdict")
            st.success(feedback["final_verdict"])

        except Exception as error:
            st.error(f"Something went wrong while generating AI feedback: {error}")

    report_text = build_download_report(
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        semantic_method=semantic_method,
        combined_score=combined_score,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        feedback=feedback,
    )

    st.session_state.report_text = report_text
    st.session_state.last_feedback = feedback

    st.download_button(
        label="Download Report (.md)",
        data=report_text,
        file_name="resume_match_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

import os
import re
import json
import math
from typing import List, Dict, Tuple, Optional

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -------------------------------
# App setup
# -------------------------------
st.set_page_config(
    page_title="Resume Matcher Pro",
    page_icon="📄",
    layout="wide",
)

# -------------------------------
# Styling
# -------------------------------
st.markdown(
    """
    <style>
        .main {
            background: linear-gradient(180deg, #0b1020 0%, #111827 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        h1, h2, h3 {
            color: #f8fafc !important;
        }
        p, label, .stMarkdown, .stCaption {
            color: #dbe4ee !important;
        }
        .app-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.18);
            margin-bottom: 1rem;
        }
        .score-card {
            background: linear-gradient(135deg, rgba(59,130,246,0.22), rgba(16,185,129,0.18));
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 18px;
            padding: 18px;
            text-align: center;
            min-height: 130px;
        }
        .score-title {
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-bottom: 0.35rem;
        }
        .score-value {
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.25rem;
        }
        .score-note {
            font-size: 0.85rem;
            color: #cbd5e1;
        }
        .small-note {
            color: #94a3b8;
            font-size: 0.9rem;
        }
        div[data-testid="stMetricValue"] {
            color: white;
        }
        div[data-testid="stFileUploader"] section {
            background: rgba(255,255,255,0.04);
            border-radius: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 Resume & Job Description Matcher")
st.caption("Upload or paste a resume, compare it to a job description, and get AI-powered improvement suggestions.")


# -------------------------------
# Session state
# -------------------------------
if "resume_input" not in st.session_state:
    st.session_state.resume_input = ""

if "job_input" not in st.session_state:
    st.session_state.job_input = ""

if "report_text" not in st.session_state:
    st.session_state.report_text = ""

if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None


# -------------------------------
# Helpers
# -------------------------------
def create_openai_client() -> Optional[OpenAI]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


COMMON_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "have", "has", "are", "you",
    "your", "will", "our", "their", "into", "using", "used", "use", "can", "able",
    "such", "across", "about", "role", "team", "work", "working", "build", "building",
    "candidate", "candidates", "experience", "years", "year", "skills", "skill",
    "knowledge", "strong", "excellent", "good", "understanding", "preferred", "plus",
    "including", "ability", "required", "requirements", "responsibilities", "job",
    "description", "resume", "cv", "support", "develop", "development", "engineer",
    "engineering", "data", "ai", "ml"
}

KNOWN_TECH_TERMS = [
    "python", "sql", "tensorflow", "pytorch", "scikit-learn", "sklearn", "pandas",
    "numpy", "matplotlib", "docker", "kubernetes", "aws", "gcp", "azure",
    "fastapi", "flask", "django", "streamlit", "langchain", "llamaindex", "rag",
    "vector database", "pinecone", "faiss", "chroma", "weaviate", "openai",
    "prompt engineering", "llm", "llms", "transformers", "hugging face", "nlp",
    "computer vision", "genai", "generative ai", "git", "github", "jupyter",
    "feature engineering", "model evaluation", "model training", "deep learning",
    "machine learning", "rest api", "api", "etl", "airflow", "spark", "linux",
    "embeddings", "semantic search"
]


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\-\+#\. ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def read_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def extract_keywords(text: str) -> List[str]:
    normalized = clean_text(text)
    found_keywords = set()

    for term in KNOWN_TECH_TERMS:
        if term in normalized:
            found_keywords.add(term)

    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\-\+#\.]{1,}", normalized)
    for token in tokens:
        if token not in COMMON_WORDS and len(token) > 2:
            found_keywords.add(token)

    return sorted(found_keywords)


def calculate_keyword_score(resume_text: str, job_text: str) -> Tuple[int, List[str], List[str]]:
    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_text))

    if not job_keywords:
        return 0, [], []

    matched = sorted(job_keywords.intersection(resume_keywords))
    missing = sorted(job_keywords.difference(resume_keywords))
    score = int((len(matched) / len(job_keywords)) * 100)

    return score, matched, missing


def calculate_tfidf_semantic_score(resume_text: str, job_text: str) -> Tuple[int, str]:
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([resume_text, job_text])
    similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    score = int(round(max(0.0, min(1.0, similarity)) * 100))
    return score, "TF-IDF cosine similarity"


def cosine_from_lists(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def trim_for_embedding(text: str, max_chars: int = 12000) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def calculate_semantic_score(
    resume_text: str,
    job_text: str,
    client: Optional[OpenAI],
) -> Tuple[int, str]:
    if client is None:
        return calculate_tfidf_semantic_score(resume_text, job_text)

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[trim_for_embedding(resume_text), trim_for_embedding(job_text)],
        )
        vec_resume = response.data[0].embedding
        vec_job = response.data[1].embedding
        similarity = cosine_from_lists(vec_resume, vec_job)
        score = int(round(max(0.0, min(1.0, similarity)) * 100))
        return score, "OpenAI embeddings"
    except Exception:
        return calculate_tfidf_semantic_score(resume_text, job_text)


def calculate_combined_score(keyword_score: int, semantic_score: int) -> int:
    return int(round((0.45 * keyword_score) + (0.55 * semantic_score)))


def detect_resume_sections(resume_text: str) -> Dict[str, str]:
    section_patterns = {
        "summary": r"(summary|profile|professional summary)",
        "skills": r"(skills|technical skills|core skills)",
        "experience": r"(experience|work experience|employment)",
        "projects": r"(projects|selected projects)",
        "education": r"(education|academic background)",
    }

    lines = resume_text.splitlines()
    sections = {}
    current_section = "general"
    buffer = []

    def save_section(section_name: str, content: List[str]) -> None:
        text = "\n".join(content).strip()
        if text:
            sections[section_name] = text

    for line in lines:
        stripped = line.strip()

        if not stripped:
            buffer.append(line)
            continue

        new_section = None
        for name, pattern in section_patterns.items():
            if re.fullmatch(pattern, stripped.lower()):
                new_section = name
                break

        if new_section:
            save_section(current_section, buffer)
            current_section = new_section
            buffer = []
        else:
            buffer.append(line)

    save_section(current_section, buffer)
    return sections


def display_keywords(items: List[str], limit: int = 30) -> str:
    if not items:
        return "None found"
    return ", ".join(items[:limit])


def get_ai_resume_feedback(
    client: OpenAI,
    resume_text: str,
    job_text: str,
    matched_keywords: List[str],
    missing_keywords: List[str],
    keyword_score: int,
    semantic_score: int,
    combined_score: int,
) -> Dict:
    system_prompt = """
You are an expert recruiter and resume coach.

Compare a candidate's resume with a job description and return:
1. a short fit summary
2. top strengths
3. top gaps
4. an improved professional summary
5. 4 ATS-friendly rewritten resume bullets
6. 5 recommended keywords to add only if truthful
7. a final verdict

Rules:
- Be clear, practical, and professional.
- Do not invent fake experience, fake numbers, or fake technologies.
- Only suggest keywords that genuinely fit the profile.
- Return valid JSON only.
"""

    user_prompt = f"""
RESUME:
{resume_text}

JOB DESCRIPTION:
{job_text}

MATCHED KEYWORDS:
{matched_keywords}

MISSING KEYWORDS:
{missing_keywords}

CURRENT SCORES:
- Keyword Score: {keyword_score}
- Semantic Score: {semantic_score}
- Combined Score: {combined_score}

Return JSON in this format:
{{
  "fit_summary": "string",
  "top_strengths": ["string", "string", "string"],
  "top_gaps": ["string", "string", "string"],
  "improved_summary": "string",
  "rewritten_bullets": ["string", "string", "string", "string"],
  "recommended_keywords": ["string", "string", "string", "string", "string"],
  "final_verdict": "string"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content or ""

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        possible_json = re.search(r"\{.*\}", content, re.DOTALL)
        if possible_json:
            return json.loads(possible_json.group(0))
        raise ValueError("The AI response could not be read as JSON.")


def build_download_report(
    keyword_score: int,
    semantic_score: int,
    semantic_method: str,
    combined_score: int,
    matched_keywords: List[str],
    missing_keywords: List[str],
    feedback: Optional[Dict],
) -> str:
    report = [
        "# Resume Match Report",
        "",
        f"- Keyword Match Score: **{keyword_score}%**",
        f"- Semantic Match Score: **{semantic_score}%**",
        f"- Semantic Method: **{semantic_method}**",
        f"- Combined Match Score: **{combined_score}%**",
        "",
        "## Matched Keywords",
        display_keywords(matched_keywords, limit=100),
        "",
        "## Missing Keywords",
        display_keywords(missing_keywords, limit=100),
        "",
    ]

    if feedback:
        report.extend([
            "## Overall Fit",
            feedback.get("fit_summary", ""),
            "",
            "## Top Strengths",
            *[f"- {item}" for item in feedback.get("top_strengths", [])],
            "",
            "## Top Gaps",
            *[f"- {item}" for item in feedback.get("top_gaps", [])],
            "",
            "## Improved Professional Summary",
            feedback.get("improved_summary", ""),
            "",
            "## Suggested Resume Bullets",
            *[f"- {item}" for item in feedback.get("rewritten_bullets", [])],
            "",
            "## Recommended Keywords",
            ", ".join(feedback.get("recommended_keywords", [])),
            "",
            "## Final Verdict",
            feedback.get("final_verdict", ""),
        ])

    return "\n".join(report)


def score_card(title: str, score: int, note: str) -> None:
    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-title">{title}</div>
            <div class="score-value">{score}%</div>
            <div class="score-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.header("Tools")
    st.write("Load sample content or upload a PDF resume.")

    if st.button("Load example resume", use_container_width=True):
        st.session_state.resume_input = EXAMPLE_RESUME

    if st.button("Load example job description", use_container_width=True):
        st.session_state.job_input = EXAMPLE_JOB

    if st.button("Load both examples", use_container_width=True):
        st.session_state.resume_input = EXAMPLE_RESUME
        st.session_state.job_input = EXAMPLE_JOB

    st.markdown("---")
    uploaded_resume = st.file_uploader("Upload resume PDF", type=["pdf"])

    if uploaded_resume is not None:
        try:
            extracted_text = read_pdf_text(uploaded_resume)
            st.success(f"PDF read successfully: {uploaded_resume.name}")
            st.caption(f"Extracted {len(extracted_text)} characters")
            if st.button("Use uploaded PDF as resume", use_container_width=True):
                st.session_state.resume_input = extracted_text
        except Exception as error:
            st.error(f"Could not read PDF: {error}")

    st.markdown("---")
    st.info("This app reads OPENAI_API_KEY from your environment. If the key is set, you'll get AI feedback and embedding-based semantic matching.")


# -------------------------------
# Main input area
# -------------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("Resume")
    st.text_area(
        "Paste resume text",
        height=420,
        key="resume_input",
        placeholder="Paste the full resume here or upload a PDF from the sidebar...",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("Job Description")
    st.text_area(
        "Paste job description text",
        height=420,
        key="job_input",
        placeholder="Paste the full job description here...",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

analyze_button = st.button("Analyze Resume Match", use_container_width=True)


# -------------------------------
# Run analysis
# -------------------------------
if analyze_button:
    resume_text = st.session_state.resume_input
    job_text = st.session_state.job_input

    if not resume_text.strip() or not job_text.strip():
        st.error("Please provide both a resume and a job description.")
        st.stop()

    client = create_openai_client()

    keyword_score, matched_keywords, missing_keywords = calculate_keyword_score(resume_text, job_text)
    semantic_score, semantic_method = calculate_semantic_score(resume_text, job_text, client)
    combined_score = calculate_combined_score(keyword_score, semantic_score)
    sections = detect_resume_sections(resume_text)

    st.subheader("Match Overview")

    c1, c2, c3 = st.columns(3)
    with c1:
        score_card("Keyword Match", keyword_score, "Direct overlap between resume and JD keywords")
    with c2:
        score_card("Semantic Match", semantic_score, semantic_method)
    with c3:
        score_card("Combined Score", combined_score, "Weighted mix of keyword and semantic signals")

    st.progress(min(combined_score, 100))

    kw_col, miss_col = st.columns(2)
    with kw_col:
        st.markdown("### Matched Keywords")
        st.write(display_keywords(matched_keywords, limit=50))

    with miss_col:
        st.markdown("### Missing Keywords")
        st.write(display_keywords(missing_keywords, limit=50))

    st.markdown("### Resume Sections Found")
    section_preview = {
        name: (text[:220] + "..." if len(text) > 220 else text)
        for name, text in sections.items()
    }
    st.json(section_preview)

    st.markdown("---")
    st.subheader("AI Suggestions")

    feedback = None
    if client is None:
        st.warning("OPENAI_API_KEY is not set, so AI feedback is disabled. Semantic score is using the local TF-IDF fallback.")
    else:
        try:
            with st.spinner("Reviewing resume and generating suggestions..."):
                feedback = get_ai_resume_feedback(
                    client=client,
                    resume_text=resume_text,
                    job_text=job_text,
                    matched_keywords=matched_keywords,
                    missing_keywords=missing_keywords,
                    keyword_score=keyword_score,
                    semantic_score=semantic_score,
                    combined_score=combined_score,
                )

            st.markdown("### Overall Fit")
            st.write(feedback["fit_summary"])

            strength_col, gap_col = st.columns(2)
            with strength_col:
                st.markdown("### Strong Points")
                for item in feedback["top_strengths"]:
                    st.write(f"- {item}")

            with gap_col:
                st.markdown("### Areas to Improve")
                for item in feedback["top_gaps"]:
                    st.write(f"- {item}")

            st.markdown("### Better Professional Summary")
            st.info(feedback["improved_summary"])

            st.markdown("### Suggested Resume Bullets")
            for bullet in feedback["rewritten_bullets"]:
                st.write(f"- {bullet}")

            st.markdown("### Keywords You Could Add")
            st.write(", ".join(feedback["recommended_keywords"]))

            st.markdown("### Final Recruiter Verdict")
            st.success(feedback["final_verdict"])

        except Exception as error:
            st.error(f"Something went wrong while generating AI feedback: {error}")

    report_text = build_download_report(
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        semantic_method=semantic_method,
        combined_score=combined_score,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        feedback=feedback,
    )

    st.session_state.report_text = report_text
    st.session_state.last_feedback = feedback

    st.download_button(
        label="Download Report (.md)",
        data=report_text,
        file_name="resume_match_report.md",
        mime="text/markdown",
        use_container_width=True,
    )


    #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
