# Software Testing and Quality Assurance (STQA) Project Report
## Mini-Project: Verification, Validation, and Quality Engineering of a Job Application and Resume Submission Portal

---

### Abstract
This project presents a rigorous Software Testing and Quality Assurance (STQA) case study conducted on an open-source, Flask-based Job Application and Resume Submission Portal. The legacy system exhibited operational defects, critical security vulnerabilities (OWASP Top 10 A01: Broken Access Control), environment incompatibilities under Python 3.13, and a total absence of automated regression and verification mechanisms. Following established quality engineering principles (IEEE 829 for test documentation and ISO/IEC/IEEE 29119 for software testing), a multi-tier testing framework was architected, incorporating unit testing with Boundary Value Analysis (BVA) and Equivalence Partitioning (EP), integration testing for HTTP workflows and session state, and headless Selenium browser automation for end-to-end user journeys. A dynamic database rebinding mechanism guarantees zero contamination of production data during automated testing. All 117 automated tests achieved a 100% pass rate, delivering 91% overall application statement coverage and 100% coverage across core database models and form validators.

---

### 1. Introduction and Problem Statement

Modern web applications handling personally identifiable information (PII) and recruitment data require stringent functional correctness, security controls, and high software quality. The investigated repository, originally created in 2021 as a Flask web application, suffered from severe quality deficiencies:
1. **Environment Incompatibility**: Outdated dependencies pinned in a UTF-16 encoded `requirements.txt` failed to install or run under modern Python (Python 3.13.1).
2. **Import-Time Crashes**: Module-level database queries executed outside of Flask's application context caused immediate `RuntimeError` crashes.
3. **Severe Security Flaws (Broken Access Control & Insecure Direct Object References)**: Unauthenticated guests and competing companies could freely view candidate resumes, confidential applicant profiles, and other employers' candidate pools.
4. **Data Integrity Hazards**: Raw upload filenames permitted silent file overwriting, while static `date.today()` defaults led to stale database timestamps.
5. **Lack of Automated Verification**: The application had zero automated tests, making refactoring and vulnerability mitigation high-risk without regression testing.

---

### 2. Project Objectives

The primary objectives of this STQA engineering project were:
1. **Stabilize and Modernize the Runtime Environment**: Modernize dependency specifications for Python 3.13 without altering core architecture or business logic.
2. **Defect Identification and Systematic Remediation**: Detect, log, prioritize, and remediate all security, runtime, and data integrity defects through a formal Defect Life Cycle.
3. **Zero Production Mutation**: Design an automated test infrastructure that guarantees absolute isolation, preserving production data (`app/site.db`) untouched.
4. **Comprehensive Multi-Tier Test Suite**:
   - Implement **Smoke Testing** to ensure basic operational readiness.
   - Implement **Unit Testing** on database models, relationships, and form validation using Equivalence Partitioning and Boundary Value Analysis.
   - Implement **Integration Testing** covering authentication, job management, candidate submissions, and role-based authorization.
   - Implement **End-to-End (E2E) Browser Automation** using Selenium WebDriver to simulate real user behavior across critical recruitment paths.
5. **Quality Metrics & Documentation**: Achieve >85% application statement coverage and provide academic deliverables including a Master Test Plan, Defect Register, Traceable Test Cases, and Interactive Test Reports.

---

### 3. Technology Stack

| Layer | Technologies & Tools |
| :--- | :--- |
| **Operating System** | Windows 11 (64-bit) |
| **Language Runtime** | Python 3.13.1 (Virtual Environment `venv`) |
| **Web Framework** | Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6 |
| **ORM & Database** | Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.4, SQLite 3 |
| **Authentication & Forms** | Flask-Login 0.6.3, Flask-Bcrypt 1.0.1, Flask-WTF 1.3.0, WTForms 3.2.2 |
| **Image Processing** | Pillow 12.3.0 |
| **Test Runners & Reporting** | Pytest 9.1.1, Pytest-HTML 4.2.0, Coverage.py 7.16.2 |
| **Browser Automation** | Selenium WebDriver 4.51.0, Headless Google Chrome (v144) |

---

### 4. Application Architecture and Features

The application operates as a dual-role recruitment portal:
- **Role 1: Job Seeker (Candidate)**:
  - Account registration and authentication.
  - Public job browsing on `/show_jobs`.
  - Application submission on `/post_cvs/<jobid>` with mandatory cover letter, qualification attributes, and image resume upload (`.png`, `.jpg`, `.bmp`).
  - View personal submitted resume on `/resume/<id>` and join interview meeting room on `/meeting/<id>`.
- **Role 2: Company (Employer / Recruiter)**:
  - Company registration and employer authentication.
  - Job posting on `/post_jobs` with industry classification and job description.
  - Employer dashboard on `/posted_jobs` displaying openings posted by the authenticated company.
  - Applicant management on `/show_applications/<jobid>` displaying candidate rankings sorted by degree and experience.
  - Candidate resume inspection on `/resume/<id>` and interview access on `/meeting/<id>`.
- **Common Features**:
  - System review submission on `/review`.
  - Random review showcase via Jinja2 context processor.

---

### 5. STQA Methodology

The project adheres to the **V-Model of Software Development and Testing**:
1. **Requirements & Code Audit**: Static analysis of routes, forms, models, and template markup to detect code smells, OWASP vulnerabilities, and architectural bugs.
2. **Defect Logging (IEEE 829)**: Registration of confirmed bugs in `test_documents/defect_register.csv` with severity, priority, and reproduction steps prior to code modification.
3. **Test Infrastructure & Isolation**: Configuration of dynamic test engine rebinding in `tests/conftest.py`, allocating temporary isolated databases on Drive E (`E:\temp\stqa_test_*.db`) and releasing locks via `engine.dispose()`.
4. **Test Case Design**:
   - **Equivalence Partitioning (EP)**: Valid vs. invalid data classes across all form inputs (e.g. valid job seekers vs. companies, valid image extensions vs. invalid executable/document extensions).
   - **Boundary Value Analysis (BVA)**: Min/max boundary testing for text lengths (username: `min=2, max=20`; job title: `min=2, max=100`).
5. **Execution & Regression Control**: Pytest markers (`@pytest.mark.smoke`, `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`) enabling selective and full regression execution.

---

### 6. Test Plan Overview

Aligned with IEEE 829 guidelines, the Master Test Plan (`test_documents/test_plan.md`) established:
- **Scope**: Functional verification of authentication, job lifecycle, file uploads, role boundaries, and web UI.
- **Entry Criteria**: Environment stabilized under Python 3.13, dependencies installed, and clean application import without exceptions.
- **Exit Criteria**: 100% test pass rate across all tiers, >85% overall coverage, zero critical/high severity defects remaining, and zero mutation of production database `app/site.db`.

---

### 7. Unit Testing

Located in `tests/unit/`, 57 unit tests verify underlying models and input validation logic in complete isolation:
- **Models (`tests/unit/test_models.py` - 16 tests)**:
  - User instantiation, unique constraints (`username`, `email`), Flask-Login `UserMixin` properties (`is_authenticated`, `is_active`, `is_anonymous`), bcrypt password hash generation and verification, and user loader callback.
  - Jobs model instantiation, dynamic timestamp generation (`datetime.now`), and string representation (`__repr__`).
  - Application model relational mappings (`job_applier`, `application_submiter`, `application_jober`).
  - Review model unique constraints and string formatting.
- **Forms (`tests/unit/test_forms.py` - 41 tests)**:
  - `RegistrationForm`: Boundary checks on username length (lengths 1, 2, 3, 19, 20, 21), email format validation, password confirmation matching, and database uniqueness checks.
  - `LoginForm`: Missing credentials, malformed emails, and remember-me toggles.
  - `JobForm`: Boundary checks on job title (lengths 1, 2, 100, 101), required description, and industry selection constraints.
  - `ApplicationForm`: Mandatory cover letter, numeric experience validation, and strict file format enforcement (`.jpg`, `.png`, `.bmp` accepted; `.pdf`, `.docx`, `.exe`, `.txt`, `.zip` rejected).
  - `ReviewForm`: Required username and text body validation.

---

### 8. Integration Testing

Located in `tests/integration/`, 45 integration tests verify HTTP request/response flows, session cookies, database state transitions, and access control:
- **Authentication Flows (`test_auth_routes.py` - 14 tests)**:
  - Complete registration HTTP POST flow and password persistence.
  - Duplicate user/email rejection and form error rendering.
  - Login authentication for Job Seeker and Company accounts with redirection to role-specific landing pages (`/show_jobs` vs `/posted_jobs`).
  - Rejection of invalid passwords, non-existent accounts, and mismatched usertypes.
  - Deep-link redirection preserving the `next` query parameter.
  - Session invalidation upon `/logout`.
- **Job Workflows (`test_job_routes.py` - 5 tests)**:
  - Company job posting creation, DB linkage to authenticated employer, and mandatory field enforcement.
  - Company dashboard privacy: verified that `/posted_jobs` strictly displays openings created by the authenticated company.
- **Application & Resume Workflows (`test_application_routes.py` - 6 tests)**:
  - Multipart resume upload with automatic randomized filename hashing (preventing file collisions and path traversal).
  - Rejection of missing files and invalid document extensions.
  - Non-existent job ID error handling.
- **Role-Based Access Control (`test_authorization.py` - 20 tests)**:
  - Verification that anonymous guests attempting to access protected endpoints (`/post_jobs`, `/posted_jobs`, `/show_applications`, `/resume`, `/meeting`, `/logout`) are redirected to login.
  - Prevention of Job Seekers accessing company-only routes.
  - Prevention of Companies applying for jobs.
  - **Cross-Tenant Isolation**: Verified that competing companies cannot view applicants or resumes belonging to another company's job postings.
  - Resume and interview room authorization: candidate and hiring employer permitted; unrelated third parties denied.

---

### 9. Selenium Browser Automation Testing

Located in `tests/e2e/`, 5 automated end-to-end browser tests simulate real user interactions in headless Google Chrome:
- **Live Test Server Architecture**: Spawns an internal `werkzeug.serving.make_server` on an ephemeral localhost port in a background thread, pointing to a dedicated temporary SQLite database.
- **Automated Scenarios**:
  1. `test_public_job_board_loads_successfully`: Browser navigates to homepage, checks responsive layout, page title, and validates that seeded job cards are visible.
  2. `test_valid_applicant_login`: Automates dropdown selection, credential entry, submit click, and verifies URL transition and presence of "Log out" button.
  3. `test_invalid_login_shows_error`: Enters incorrect password and asserts that Bootstrap alert feedback (`.alert-danger`) renders with appropriate user warning.
  4. `test_unauthenticated_access_to_protected_page_redirects`: Tests navigation to `/post_jobs` and asserts browser URL redirection to login with query parameters.
  5. `test_job_application_submission_with_valid_resume`: Logs in as candidate, navigates to application form, selects qualifications, inputs experience and cover letter, uploads a generated test PNG image, scrolls submit button into view, submits, and asserts success alert and database persistence.

---

### 10. Test Case Traceability Summary

All 83 formal test cases documented in `test_documents/test_cases.csv` directly trace to implemented tests:

| Category | Test Case IDs | Verification Level | Status |
| :--- | :--- | :--- | :---: |
| Environment & Isolation | TC-ENV-01 to TC-ENV-02 | Smoke / Integrity | **Pass (100%)** |
| User Model | TC-MOD-01 to TC-MOD-08 | Unit / ORM | **Pass (100%)** |
| Jobs Model | TC-MOD-09 to TC-MOD-11 | Unit / ORM | **Pass (100%)** |
| Application Model | TC-MOD-12 to TC-MOD-13 | Unit / ORM | **Pass (100%)** |
| Review Model | TC-MOD-14 to TC-MOD-16 | Unit / ORM | **Pass (100%)** |
| Registration Form | TC-FORM-01 to TC-FORM-13 | Unit / BVA & EP | **Pass (100%)** |
| Login Form | TC-FORM-14 to TC-FORM-16 | Unit / EP | **Pass (100%)** |
| Job Form | TC-FORM-17 to TC-FORM-23 | Unit / BVA & EP | **Pass (100%)** |
| Application Form | TC-FORM-24 to TC-FORM-29 | Unit / EP & Upload | **Pass (100%)** |
| Review Form | TC-FORM-30 to TC-FORM-32 | Unit / EP | **Pass (100%)** |
| Authentication Integration | TC-AUTH-01 to TC-AUTH-11 | Integration / Flow | **Pass (100%)** |
| Job Management Integration | TC-JOB-01 to TC-JOB-04 | Integration / Flow | **Pass (100%)** |
| Application Integration | TC-APP-01 to TC-APP-07 | Integration / Flow | **Pass (100%)** |
| Access Control & Security | TC-SEC-01 to TC-SEC-08 | Integration / Auth | **Pass (100%)** |
| End-to-End Automation | TC-E2E-01 to TC-E2E-05 | System / Selenium | **Pass (100%)** |

---

### 11. Defect Management and Resolution History

All identified defects were tracked in `test_documents/defect_register.csv` and resolved with verifiable code solutions:

| Defect ID | Component | Summary | Severity | Status | Resolution |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **DEF-001** | `app/routes.py` | Module-level `Review.query.all()` caused `RuntimeError: Working outside of application context`. | Critical | Fixed | Encapsulated query inside dynamic helper `get_random_reviews()` and Jinja context processor. |
| **DEF-002** | `app/routes.py` | Resume filename collisions and overwrites due to raw filename usage in `save_picture()`. | High | Fixed | Generated collision-resistant 16-hex token prefixed filename with lowercase extension. |
| **DEF-003** | `app/forms.py` & `routes.py` | Missing-file submission caused unhandled `AttributeError` (HTTP 500) in `post_cvs`. | High | Fixed | Added `FileRequired` validator to `cv` field in `forms.py` and defensive checks in `routes.py`. |
| **DEF-004** | `app/routes.py` | Broken Access Control (OWASP A01): Logged-in users could view applicants for any job. | High | Fixed | Enforced role check for `Company` and verified `job.user_id == current_user.id`. |
| **DEF-005** | `app/routes.py` | Insecure Direct Object Reference (OWASP A01): Resume images accessible without authentication. | High | Fixed | Added `@login_required` and validated ownership (applicant ID or company employer ID). |
| **DEF-006** | `app/models.py` | `date_posted` default evaluated once at module import instead of dynamically per record. | Medium | Fixed | Changed `default=date.today()` to callable `default=datetime.now` without invocation parentheses. |
| **DEF-007** | `app/templates/layout.html` | Broken mod_pagespeed scripts caused browser console errors and styling glitches. | Low | Fixed | Cleaned obsolete scraped scripts; linked clean local `style.css` and Bootstrap 5 bundle. |
| **DEF-008** | `requirements.txt` | Outdated 2021 dependencies and UTF-16 LE encoding broke Python 3.13 installation. | High | Fixed | Modernized requirements to Python 3.13-compatible pins with standard UTF-8 encoding. |

---

### 12. Actual Test Results & Code Coverage

#### Test Execution Totals (Execution Date: October 15, 2026)
- **Total Tests Collected**: 117
- **Passed**: 117 (100%)
- **Failed**: 0
- **Skipped**: 0
- **Errors**: 0
- **Total Execution Time**: 63.30 seconds
- **Warnings**: 33 benign third-party deprecation warnings regarding `datetime.utcnow()` inside `flask_login/login_manager.py`.

#### Final Statement Coverage
Measured via `coverage.py 7.16.2`:
```
Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
app\__init__.py      15      0   100%
app\forms.py         43      0   100%
app\models.py        46      0   100%
app\routes.py       180     25    86%   32-34, 56-57, 78, 121-122, 165-176, 197-198, 202-205, 213-214
-----------------------------------------------
TOTAL               284     25    91%
```

- **Interactive Test Report**: `reports/test_report.html`
- **Interactive Code Coverage Report**: `reports/coverage/index.html`

---

### 13. System Limitations

1. **Temporary Twilio Video Mock**: The `/meeting/<id>` endpoint renders the interview UI with Twilio Video CDN scripts, but actual live video calls require active third-party Twilio API credentials.
2. **Resume Format Restriction**: The portal accepts image-based resumes (`.jpg`, `.png`, `.bmp`) processed via Pillow. Standard document formats (`.pdf`, `.docx`) are intentionally rejected by form validation; future enhancements could integrate document parsers.
3. **C Drive Storage Constraints**: When running on machines with low free space on Drive C (<50 MB), tests must be executed with temporary files directed to secondary storage (`E:\temp`) via `conftest.py`.

---

### 14. Conclusion and Future Scope

This STQA mini-project successfully transformed a broken, vulnerable, and unverified legacy web application into a stable, secure, and rigorously tested software system. Through systematic defect resolution, 117 automated tests across unit, integration, and Selenium E2E tiers, and 91% code coverage, software quality and reliability have been comprehensively validated.

**Future Scope**:
- Integration of PDF parsing and text extraction for resume submissions.
- Implementation of automated Continuous Integration (CI) pipelines using GitHub Actions.
- Load and stress testing using Locust to evaluate concurrency under high applicant traffic.
