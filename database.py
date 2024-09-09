import sqlite3
from dotenv import load_dotenv

load_dotenv()

class SQLiteDB:
    def __init__(self):
        self.conn = sqlite3.connect('resume_matcher.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY,
            title TEXT,
            skills TEXT,
            min_experience_years REAL,
            max_experience_years REAL,
            min_budget_lpa REAL,
            max_budget_lpa REAL,
            location_requirement TEXT,
            work_mode TEXT,
            description TEXT
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            mobile_no TEXT,
            skills TEXT,
            experience_years REAL,
            relevant_experience_years REAL,
            current_ctc_lpa REAL,
            expected_ctc_lpa REAL,
            notice_period_months INTEGER,
            work_mode TEXT,
            location TEXT,
            resume_text TEXT
        )
        ''')
        self.conn.commit()

    def add_job_description(self, title, skills, min_experience_years, max_experience_years, min_budget_lpa, 
                            max_budget_lpa, location_requirement, work_mode, description):
        self.cursor.execute('''
        INSERT INTO job_descriptions (title, skills, min_experience_years, max_experience_years, min_budget_lpa,
                                      max_budget_lpa, location_requirement, work_mode, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, skills, min_experience_years, max_experience_years, min_budget_lpa,
              max_budget_lpa, location_requirement, work_mode, description))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_candidate(self, name, email, mobile_no, skills, experience_years, relevant_experience_years, 
                      current_ctc_lpa, expected_ctc_lpa, notice_period_months, work_mode, location, resume_text):
        self.cursor.execute('''
        INSERT INTO candidates (name, email, mobile_no, skills, experience_years, relevant_experience_years,
                                current_ctc_lpa, expected_ctc_lpa, notice_period_months, work_mode, location, resume_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, mobile_no, skills, experience_years, relevant_experience_years,
              current_ctc_lpa, expected_ctc_lpa, notice_period_months, work_mode, location, resume_text))
        self.conn.commit()
        return self.cursor.lastrowid

    def fetch_all_candidates(self):
        self.cursor.execute('SELECT * FROM candidates')
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def fetch_all_job_descriptions(self):
        self.cursor.execute('SELECT * FROM job_descriptions')
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

db = SQLiteDB()

def init_db():
    # Database is initialized when SQLiteDB is instantiated
    pass

# Use these functions in your application
add_job_description = db.add_job_description
add_candidate = db.add_candidate
fetch_all_candidates = db.fetch_all_candidates
fetch_all_job_descriptions = db.fetch_all_job_descriptions