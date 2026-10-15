# STQA Mini-Project: System Demonstration Guide

This guide provides step-by-step instructions for running the Job Application and Resume Submission Portal and demonstrating the test suites, security controls, and quality reports.

---

## 1. How to Start the Application

### Prerequisites
- Python 3.13 virtual environment (`venv`) active.
- Terminal opened at project root: `E:\LP4 mini prj\Python_Flask_Job_Portal`.

### Launching the Development Server
Run the application using the virtual environment Python interpreter:
```powershell
.\venv\Scripts\python.exe run.py
```
The server will start at: **`http://127.0.0.1:5000`**

---

## 2. Interactive Feature Demonstration

### Step 1: Public Job Browsing
1. Open browser and visit: `http://127.0.0.1:5000/`
2. **Observe**:
   - Navigation header displaying "Job Portal", "Sign Up", and "Log in".
   - Dynamic testimonials carousel displaying community reviews.
   - Public job board displaying available job openings across companies.

### Step 2: Job Seeker Journey (Applying for a Job)
1. Click **Sign Up** (or visit `/register`):
   - Select **User Type**: `Job Seeker`
   - Enter a new username (e.g. `DemoSeeker`), unique email, password, and confirmation password.
   - Submit. You will be redirected to the login page with a green success alert.
2. Log In as Job Seeker:
   - Select **User Type**: `Job Seeker`
   - Enter your email and password.
   - Click **Log In**. You are redirected to `/show_jobs`.
3. Apply for an Opening:
   - Click the **Apply** button on any job card (navigates to `/post_cvs/<jobid>`).
   - Select **Gender**, **Degree**, and **Industry**.
   - Enter **Experience** (in years, e.g. `3`).
   - Enter **Cover Letter** text.
   - Upload an image resume file (`.png`, `.jpg`, or `.bmp`).
   - Click **Submit**.
   - **Observe**: You are redirected to `/show_jobs` with the confirmation alert *"Your application has been submitted successfully!"*.

### Step 3: Company Journey (Job Management & Candidate Review)
1. Log out using the **Log out** button in the header.
2. Log In as a Company:
   - Click **Log in** (`/login`).
   - Select **User Type**: `Company`.
   - Enter seeded company credentials:
     - **Email**: `Google@gmail.com`
     - **Password**: *(or register a new Company account via `/register`)*
3. View Posted Jobs Dashboard:
   - **Observe**: Company is routed to `/posted_jobs`, showing only jobs posted by this company.
4. Post a New Job:
   - Click **Post a job** (`/post_jobs`).
   - Enter Job Title, Industry, and Description.
   - Click **Submit**. The job is immediately listed on the dashboard.
5. Review Candidate Applications:
   - Click **Applications** on your posted job card (`/show_applications/<jobid>`).
   - View applicants sorted by degree level and years of experience.
   - Click **See Resume** (`/resume/<id>`) to view the applicant's uploaded credential.

---

## 3. Demonstrating Security & Authorization Controls

1. **Unauthenticated Access Protection**:
   - In an incognito window without logging in, try opening:
     `http://127.0.0.1:5000/post_jobs`
   - **Result**: Immediately blocked and redirected to `/login?next=%2Fpost_jobs`.
2. **Role Separation**:
   - Log in as a Job Seeker and manually navigate to:
     `http://127.0.0.1:5000/post_jobs`
   - **Result**: Access denied with flash warning: *"Only registered companies can post job openings."*
3. **Cross-Company Tenant Isolation**:
   - Log in as Company A and attempt to access `/show_applications/<job_id_of_company_B>`.
   - **Result**: Access denied with danger alert: *"Access denied. You can only view applications for jobs posted by your company."*

---

## 4. Running the Automated Test Suite

All tests execute in complete isolation using temporary SQLite databases. **`app/site.db` is never modified.**

### 1. Run Quick Smoke Tests (10 tests)
```powershell
.\venv\Scripts\pytest.exe -v tests/test_smoke.py
```

### 2. Run Unit Tests (57 tests)
```powershell
.\venv\Scripts\pytest.exe -v tests/unit/
```

### 3. Run Integration Tests (45 tests)
```powershell
.\venv\Scripts\pytest.exe -v tests/integration/
```

### 4. Run Selenium E2E Headless Browser Tests (5 tests)
```powershell
.\venv\Scripts\pytest.exe -v tests/e2e/
```

### 5. Run the Entire Test Suite with Interactive HTML Report (117 tests)
```powershell
.\venv\Scripts\pytest.exe -v tests/ --html=reports/test_report.html --self-contained-html
```

---

## 5. Inspecting Generated Quality & Coverage Reports

1. **Interactive HTML Test Execution Report**:
   Open in browser:
   ```powershell
   Start-Process reports/test_report.html
   ```
   - Displays all 117 tests with execution status, timings, test IDs, and environment metadata.
2. **Interactive Code Coverage Report**:
   Open in browser:
   ```powershell
   Start-Process reports/coverage/index.html
   ```
   - Displays 91% total application statement coverage, with 100% coverage on `models.py`, `forms.py`, and `__init__.py`.
3. **Formal STQA Documentation**:
   - **Master Test Plan**: `test_documents/test_plan.md`
   - **Traceable Test Cases**: `test_documents/test_cases.csv`
   - **Defect Register**: `test_documents/defect_register.csv`
   - **Academic Project Report**: `test_documents/academic_project_report.md`
