import openai
from dotenv import load_dotenv
import os
import PyPDF2
import docx
import re
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone
import vector_store as vs

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "resume-matcher"

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_resume(file):
    text = ""
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def parse_resume(resume_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that parses resumes."},
            {"role": "user", "content": f"Parse the following resume and extract key skills and experience: {resume_text}"}
        ]
    )
    return response.choices[0].message['content']

def match_resume_to_job(job_description, candidates):
    job_embedding = vs.get_embedding(job_description['description'])
    matches = []

    for candidate in candidates:
        # Calculate vector similarity score
        candidate_embedding = vs.get_embedding(candidate['resume_text'])
        vector_similarity = util.pytorch_cos_sim(job_embedding, candidate_embedding).item()

        # Calculate skill match score
        job_skills = set(skill.strip().lower() for skill in job_description['skills'].split(','))
        candidate_skills = set(skill.strip().lower() for skill in candidate['skills'].split(','))
        matching_skills = job_skills.intersection(candidate_skills)
        skill_score = len(matching_skills) / len(job_skills) if job_skills else 0

        # Calculate experience match score
        exp_score = 0
        if job_description['min_experience_years'] <= candidate['experience_years'] <= job_description['max_experience_years']:
            exp_score = 1
        elif candidate['experience_years'] > job_description['max_experience_years']:
            exp_score = 0.5
        
        # Calculate location match score
        location_score = 1 if job_description['location_requirement'].lower() in candidate['location'].lower() else 0

        # Calculate work mode match score
        work_mode_score = 1 if candidate['work_mode'] == job_description['work_mode'] else 0

        # Calculate CTC match score
        ctc_score = 0
        if candidate['expected_ctc_lpa'] <= job_description['max_budget_lpa']:
            ctc_score = 1
        elif job_description['max_budget_lpa'] < candidate['expected_ctc_lpa'] <= (job_description['max_budget_lpa'] + 2):
            ctc_score = 0.5

        # Calculate overall match score (you can adjust weights as needed)
        overall_score = (
            vector_similarity * 0.3 +
            skill_score * 0.3 +
            exp_score * 0.15 +
            location_score * 0.1 +
            work_mode_score * 0.1 +
            ctc_score * 0.05
        )

        if overall_score > 0.5:  # Only include matches with score > 0.50
            matches.append({
                'candidate': candidate,
                'score': overall_score,
                'vector_similarity': vector_similarity,
                'skill_score': skill_score,
                'exp_score': exp_score,
                'location_score': location_score,
                'work_mode_score': work_mode_score,
                'ctc_score': ctc_score
            })

    # Sort matches by overall score in descending order
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    return matches

def create_index_if_not_exists():
    vs.create_index_if_not_exists()

# Use the functions from vector_store.py for Pinecone operations
upsert_resume = vs.upsert_resume
delete_resume = vs.delete_resume