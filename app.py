import streamlit as st
import database as db
import ai_matcher as ai
import pandas as pd
from datetime import datetime
import math
import html

# Initialize the database
db.init_db()
ai.create_index_if_not_exists()

def main():
    st.title("Resume Matcher")

    menu = ["Home", "Job Descriptions", "Candidates", "Match Resumes"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Welcome to Resume Matcher")
        st.write("Use the sidebar to navigate through different functionalities.")

    elif choice == "Job Descriptions":
        job_descriptions_page()

    elif choice == "Candidates":
        candidates_page()

    elif choice == "Match Resumes":
        match_resumes_page()

def job_descriptions_page():
    st.subheader("Job Descriptions")
    
    tab1, tab2, tab3 = st.tabs(["Add New", "View All", "Bulk Import"])
    
    with tab1:
        add_job_description()
    
    with tab2:
        view_job_descriptions()
    
    with tab3:
        bulk_import_job_descriptions()

def add_job_description():
    st.subheader("Add a New Job Description")
    title = st.text_input("Job Title")
    skills = st.text_area("Required Skills")
    min_experience_years = st.number_input("Minimum Experience (Years)", min_value=0.0, step=0.5)
    max_experience_years = st.number_input("Maximum Experience (Years)", min_value=0.0, step=0.5)
    min_budget_lpa = st.number_input("Minimum Budget per Annum (lac)", min_value=0.0, step=0.1)
    max_budget_lpa = st.number_input("Maximum Budget per Annum (lac)", min_value=0.0, step=0.1)
    location_requirement = st.text_input("Location Requirement")
    work_mode = st.selectbox("Expected Work Mode", ["Remote", "Hybrid", "On location"])
    description = st.text_area("Job Description")

    if st.button("Add Job Description"):
        job_id = db.add_job_description(title, skills, min_experience_years, max_experience_years, min_budget_lpa, 
                                        max_budget_lpa, location_requirement, work_mode, description)
        st.success(f"Job Description Added Successfully with ID: {job_id}")

def view_job_descriptions():
    st.subheader("View All Job Descriptions")
    if 'job_descriptions_updated' not in st.session_state:
        st.session_state.job_descriptions_updated = False
    
    if st.session_state.job_descriptions_updated:
        st.session_state.job_descriptions_updated = False
        st.session_state.job_descriptions = db.fetch_all_job_descriptions()
    
    if 'job_descriptions' not in st.session_state:
        st.session_state.job_descriptions = db.fetch_all_job_descriptions()
    
    job_descriptions = st.session_state.job_descriptions
    
    if job_descriptions:
        df = pd.DataFrame(job_descriptions)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No job descriptions found.")

def bulk_import_job_descriptions():
    st.subheader("Bulk Import Job Descriptions")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="job_desc_upload")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        
        required_columns = ['title', 'skills', 'min_experience_years', 'max_experience_years', 
                            'min_budget_lpa', 'max_budget_lpa', 'location_requirement', 'work_mode', 'description']
        
        if not all(col in data.columns for col in required_columns):
            st.error(f"CSV must contain the following columns: {', '.join(required_columns)}")
            return
        
        if st.button("Import Job Descriptions"):
            for _, row in data.iterrows():
                db.add_job_description(
                    row['title'], row['skills'], row['min_experience_years'], row['max_experience_years'],
                    row['min_budget_lpa'], row['max_budget_lpa'], row['location_requirement'],
                    row['work_mode'], row['description']
                )
            
            st.success(f"Successfully imported {len(data)} job descriptions")
            st.session_state.job_descriptions_updated = True
            st.experimental_rerun()

def candidates_page():
    st.subheader("Candidates")
    
    tab1, tab2, tab3 = st.tabs(["Add New", "View All", "Bulk Import"])
    
    with tab1:
        add_candidate()
    
    with tab2:
        view_candidates()
    
    with tab3:
        bulk_import_candidates()

def add_candidate():
    st.subheader("Add a New Candidate")
    name = st.text_input("Candidate Name")
    email = st.text_input("Candidate Email")
    mobile_no = st.text_input("Mobile No.")
    skills = st.text_area("Skills")
    experience_years = st.number_input("Experience (Years)", min_value=0.0, step=0.5)
    relevant_experience_years = st.number_input("Relevant Experience (Years)", min_value=0.0, step=0.5)
    current_ctc_lpa = st.number_input("Current CTC / Annum (lac)", min_value=0.0, step=0.1)
    expected_ctc_lpa = st.number_input("Expected CTC / Annum (lac)", min_value=0.0, step=0.1)
    notice_period_months = st.number_input("Notice Period (Months)", min_value=0, step=1)
    work_mode = st.selectbox("Work Mode", ["Remote", "Hybrid", "On location"])
    location = st.text_input("Location")
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])
    
    if resume:
        resume_text = ai.extract_text_from_resume(resume)
    else:
        resume_text = st.text_area("Or Paste Resume Text")

    if st.button("Add Candidate"):
        candidate_id = db.add_candidate(name, email, mobile_no, skills, experience_years, relevant_experience_years, 
                                        current_ctc_lpa, expected_ctc_lpa, notice_period_months, work_mode, location, resume_text)
        ai.upsert_resume(candidate_id, resume_text)
        st.success(f"Candidate Added Successfully with ID: {candidate_id}")

def view_candidates():
    st.subheader("View All Candidates")
    if 'candidates_updated' not in st.session_state:
        st.session_state.candidates_updated = False
    
    if st.session_state.candidates_updated:
        st.session_state.candidates_updated = False
        st.session_state.candidates = db.fetch_all_candidates()
    
    if 'candidates' not in st.session_state:
        st.session_state.candidates = db.fetch_all_candidates()
    
    candidates = st.session_state.candidates
    
    if candidates:
        df = pd.DataFrame(candidates)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No candidates found.")


def bulk_import_candidates():
    st.subheader("Bulk Import Candidates")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="candidate_upload")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        
        required_columns = ['name', 'email', 'mobile_no', 'skills', 'experience_years', 'relevant_experience_years',
                            'current_ctc_lpa', 'expected_ctc_lpa', 'notice_period_months', 'work_mode', 'location', 'resume_text']
        
        if not all(col in data.columns for col in required_columns):
            st.error(f"CSV must contain the following columns: {', '.join(required_columns)}")
            return
        
        if st.button("Import Candidates"):
            for _, row in data.iterrows():
                candidate_id = db.add_candidate(
                    row['name'], row['email'], row['mobile_no'], row['skills'], row['experience_years'],
                    row['relevant_experience_years'], row['current_ctc_lpa'], row['expected_ctc_lpa'],
                    row['notice_period_months'], row['work_mode'], row['location'], row['resume_text']
                )
                ai.upsert_resume(candidate_id, row['resume_text'])
            
            st.success(f"Successfully imported {len(data)} candidates")
            st.session_state.candidates_updated = True
            st.experimental_rerun()

def match_resumes_page():
    st.subheader("Match Resumes to Job Descriptions")
    
    job_descriptions = db.fetch_all_job_descriptions()
    
    if job_descriptions:
        selected_job = st.selectbox(
            "Select a Job Description",
            job_descriptions,
            format_func=lambda x: f"ID: {x['id']} - {x['title']}"
        )
        
        st.subheader("Job Description Requirements")
        st.write(f"Title: {selected_job['title']}")
        st.write(f"Skills: {selected_job['skills']}")
        st.write(f"Experience: {selected_job['min_experience_years']} - {selected_job['max_experience_years']} years")
        st.write(f"Budget: {selected_job['min_budget_lpa']} - {selected_job['max_budget_lpa']} LPA")
        st.write(f"Location: {selected_job['location_requirement']}")
        st.write(f"Work Mode: {selected_job['work_mode']}")
        st.write(f"Description: {selected_job['description']}")
        
        if st.button("Match Resumes"):
            candidates = db.fetch_all_candidates()
            
            matches = ai.match_resume_to_job(selected_job, candidates)  # Pass the entire selected_job dictionary
            
            # Rest of the function remains the same
            # ...
            
            if matches:
                st.subheader("Matching Candidates (Score > 0.50)")
                
                # Prepare data for the table
                table_data = []
                for match in matches:
                    candidate = match['candidate']
                    score = match['score']
                    
                    # Generate detailed reasons for matching
                    def get_experience_reason():
                        if selected_job['min_experience_years'] <= candidate['experience_years'] <= selected_job['max_experience_years']:
                            return f"Candidate's experience ({candidate['experience_years']} years) is within the required range"
                        elif candidate['experience_years'] > selected_job['max_experience_years']:
                            return f"Candidate is overqualified with {candidate['experience_years']} years of experience"
                        else:
                            return f"Candidate's experience ({candidate['experience_years']} years) is below the minimum requirement"

                    reasons = [
                        f"Skills Match: Candidate possesses {len([skill for skill in selected_job['skills'].split(',') if skill.lower() in candidate['skills'].lower()])} out of {len(selected_job['skills'].split(','))} required skills.",
                        f"Experience: {get_experience_reason()}",
                        f"Work Mode: {'Matches' if candidate['work_mode'] == selected_job['work_mode'] else 'Differs from'} the job requirement.",
                        f"Location: {'Matches' if selected_job['location_requirement'].lower() in candidate['location'].lower() else 'Differs from'} the job requirement.",
                        f"AI-based Similarity: The candidate's resume has a {score:.2f} similarity score with the job description."
                    ]
                    
                    # Format reasons as HTML
                    reason_html = "<ul>" + "".join([f"<li>{html.escape(r)}</li>" for r in reasons]) + "</ul>"
                    
                    # Determine CTC/Budget match
                    if candidate['expected_ctc_lpa'] <= selected_job['max_budget_lpa']:
                        ctc_match = "Matching"
                    elif selected_job['max_budget_lpa'] < candidate['expected_ctc_lpa'] <= (selected_job['max_budget_lpa'] + 2):
                        ctc_match = "Near Matching"
                    else:
                        ctc_match = "Not Matching"
                    
                    table_data.append({
                        "Candidate ID": candidate['id'],
                        "Name": candidate['name'],
                        "Match Score": f"{score:.2f}",
                        "Skills": candidate['skills'],
                        "Experience": f"{candidate['experience_years']} years",
                        "Location": candidate['location'],
                        "Work Mode": candidate['work_mode'],
                        "Expected CTC": f"{candidate['expected_ctc_lpa']} LPA",
                        "CTC Match": ctc_match,
                        "Matching Reasons": reason_html
                    })
                
                # Create DataFrame
                df = pd.DataFrame(table_data)
                
                # Display the table with horizontal scrolling and HTML rendering
                st.markdown(
                    """
                    <style>
                    .scrollable-table {
                        overflow-x: auto;
                        max-width: 100%;
                    }
                    .scrollable-table table {
                        width: auto;
                    }
                    .dataframe {
                        font-size: 12px;
                    }
                    .dataframe th, .dataframe td {
                        white-space: nowrap;
                        padding: 8px;
                        text-align: left;
                        border-bottom: 1px solid #ddd;
                    }
                    .dataframe th {
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }
                    .dataframe tr:nth-child(even) {
                        background-color: #f9f9f9;
                    }
                    .dataframe tr:hover {
                        background-color: #f5f5f5;
                    }
                    .dataframe td:nth-child(10) {  /* Matching Reasons column */
                        min-width: 600px;
                        max-width: 1000px;
                        white-space: normal;
                    }
                    .dataframe ul {
                        padding-left: 20px;
                        margin: 0;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                # Wrap the table in a div for horizontal scrolling
                st.markdown('<div class="scrollable-table">', unsafe_allow_html=True)
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.write(f"Total matching candidates: {len(df)}")
                
            else:
                st.write("No candidates found with a match score greater than 0.50 for this job description.")
    else:
        st.write("No job descriptions available. Please add a job description first.")

if __name__ == "__main__":
    main()