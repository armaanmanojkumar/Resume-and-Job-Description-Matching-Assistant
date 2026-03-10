# Resume and Job Description Matching Assistant

An AI-powered application that compares a resume against a job description and generates recruiter-style feedback.

# Features

- Upload resume as PDF
- Paste resume text and job description
- Keyword based match scoring
- Semantic similarity scoring
- Combined resume job match score
- Matched and missing keyword analysis
- AI-generated feedback using OpenAI
- Improved professional summary suggestions
- Resume bullet rewriting
- Downloadable report

## Tech Stack

- Python
- Streamlit
- OpenAI API
- PyPDF
- scikit-learn

## How It Works

The app evaluates a resume in two ways:

1. **Keyword Matching**
   - Extracts technical and relevant terms
   - Compares resume keywords with job description keywords

2. **Semantic Matching**
   - Uses OpenAI embeddings when an API key is available
   - Falls back to TF-IDF cosine similarity if no API key is set

It then generates recruiter-style feedback, including:
- fit summary
- strengths
- gaps
- improved summary
- rewritten bullets
- keyword recommendations

## Installation

Clone the repository:

```bash
git clone https://github.com/armaanmanojkumar/Resume-and-Job-Description-Matching-Assistant.git
cd Resume-and-Job-Description-Matching-Assistant
